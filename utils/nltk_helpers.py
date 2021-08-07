# Used for NLP
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import ne_chunk
from nltk import pos_tag
import nltk
import json
import timeit
from typing import Union
import spacy

def unstops(*args) -> Union[str, list]:
	"""Takes any number of strings or lists of tokens 
	and removes all stopwords as per the English stopwords corpus.

	Raises:
		TypeError: If the argument given is not a string or list,
		the function will throw an error.

	Returns:
		results: Either a string or a list, depending on the number
		of arguments. It will be a string if a single argument is given
		or a list if multiple were given. 
	"""
	stops = set(stopwords.words('english'))
	results = []
	for arg in args:
		if type(arg) == str:
			tokens = word_tokenize(arg)
			filtered_words = [word for word in tokens if word not in stops]
			results.append(" ".join(filtered_words))
		elif type(arg) == list:
			filtered_words = [word for word in arg if word not in stops]
			results.append(" ".join(filtered_words))
		else:
			raise TypeError("Arguments must be of type str or list.")
	if len(results) == 1:
		return results[0]
	return results

def update_tokens(new_data: dict, tokens_directory: str):
	data = None
	with open(tokens_directory) as f:
		data = json.load(f)

	data.update(new_data)
	with open(tokens_directory, 'w') as f:
		json.dump(data, f)

def get_entities(text: str, sep_objs=True):
	"""Fetches entities & relevant data from a text argument. Return type will be an object
	that compiles all of the entities, labels, starts, and ends in their own lists, or a list
	of objects that each have an entity, label, start, and end if sep_objs (separate objects) is true.

	Args:
		text (str): The text to be processed.
		sep_objs (bool, optional): If set to True, function will return a list
		of objects each with an entity, label, start, and end property. Defaults to True.

	Returns:
		[type]: Object with entity/label/start/end lists, or list of objects with
		entity/label/start/end properties.
	"""
	nlp = spacy.load('en_core_web_sm')
	doc = nlp(text)
	entities = []
	labels = []
	position_start = []
	position_end = []

	if sep_objs:
		objs = []
		for ent in doc.ents:
			entity_name = unstops(str(ent))
			if entity_name in entities:
				continue
			entities.append(entity_name)
			objs.append({
				"entity": entity_name,
				"label": ent.label_,
				"start": ent.start_char,
				"end": ent.end_char
			})
		return objs

	for ent in doc.ents:
		entity_name = unstops(str(ent))
		if entity_name not in entities:
			entities.append(unstops(str(ent)))

		labels.append(ent.label_)
		position_start.append(ent.start_char)
		position_end.append(ent.end_char)
	
	return {
		"entities" : entities,
		"labels" : labels,
		"position_start" : position_start,
		"position_end" : position_end
	}

def search_tokens(query_string:str, tokens_path:str):
	"""Searches the tokens JSON in the tokens_path directory for
	files that have an entity that contains the query_string argument in its string.
	Files that are matched have their filenames appended to a results array.

	Args:
		query_string (str): The keyword/s that will be used for searching.
		tokens_path (str): Path to the file that contains the tokens.

	Returns:
		[results]: An array containing the filenames of the files that have
		entities containing the search string.
	"""
	results = []
	with open(tokens_path, 'r') as f:
		data = json.load(f)
		for filename, obj in data.items():
			print("Searching through", filename)
			entities = obj['entities']
			entity_count = len(entities)
			for i in range(min(entity_count, 20)):
				search_target = entities[i]['entity'].lower()
				query_string = query_string.lower()
				print("QUERY STRING", query_string)
				if query_string in search_target or query_string.strip() == "":
					print("Found a match for", query_string, "in", filename)
					results.append(filename)
					break
	return results


if __name__ == "__main__":
	search_tokens("huang", "../tokens.json")