from flask import Flask, render_template, flash, request, redirect, abort
from flask.helpers import send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
import pdftotext
from utils import nltk_helpers as nltk_h
import json

ALLOWED_EXTENSIONS = {'pdf'}
TOKENS_PATH = "./tokens.json"

app = Flask(__name__)
UPLOAD_FOLDER = app.root_path + ("\\public\\uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TOKENS_PATH'] = TOKENS_PATH

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
	text_from_pdf = None
	submitted = False
	if request.method == "POST":
		if 'file' not in request.files:
			flash("No file part")
			return redirect(request.url)
		file = request.files['file']
		if file.filename == "":
			flash("No selected file")
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(upload_path)
			submitted = True
			with open(upload_path, 'rb') as f:
				pdf = pdftotext.PDF(f, "secret")
				text_from_pdf = "\n\n".join(pdf)
				nltk_h.update_tokens({
					filename: {
						"entities": nltk_h.get_entities(text_from_pdf)
					}
				}, app.config['TOKENS_PATH'])

	return render_template("index.html", got_file=text_from_pdf, submitted=submitted)

@app.route("/search")
def search():
	q = None
	results = []
	if 'q' in request.args:
		q = request.args['q']
	if q != None:
		results = nltk_h.search_tokens(q, app.config['TOKENS_PATH'])
	return render_template('search.html', query=q, results=results)

@app.route("/get_file/<filename>")
def fetch_file(filename):
	download = not "view" in request.args
	try:
		return send_from_directory(app.config['UPLOAD_FOLDER'], path=filename, as_attachment=download)
	except FileNotFoundError:
		abort(404)

app.run(debug=True)
