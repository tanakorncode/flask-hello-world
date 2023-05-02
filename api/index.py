from flask import Flask
from pathlib import Path
from typing import Union, Literal, List
from PyPDF2 import PdfWriter, PdfReader
from flask_restful import Resource, Api

import os
import sys
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
from os.path import join

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def watermark(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    password: str,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    if(password):
        reader = PdfReader(content_pdf, False, password)
    else:
        reader = PdfReader(content_pdf)

    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))

    writer = PdfWriter(content_pdf)
    for index in page_indices:
        content_page = reader.pages[index]
        mediabox = content_page.mediabox

        # You need to load it again, as the last time it was overwritten
        reader_stamp = PdfReader(stamp_pdf)
        image_page = reader_stamp.pages[0]

        image_page.merge_page(content_page)
        image_page.mediabox = mediabox
        writer.add_page(image_page)

    with open(pdf_result, "wb") as fp:
        writer.write(fp)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/watermark-pdf', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(join(app.config['UPLOAD_FOLDER'], filename))
            os.chmod(join(app.config['UPLOAD_FOLDER'], filename), 0o0777)
            os.chmod(join(app.config['UPLOAD_FOLDER']), 0o0777)

            watermark(join(app.config['UPLOAD_FOLDER'], filename), join('files', request.form.get(
                'template')), join('files', "pdf_result.pdf"), request.form.get('password'))
            return send_file(join('..', 'files', "pdf_result.pdf"), mimetype='application/pdf')
            # return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


@app.route('/about')
def about():
    return 'About'

# if __name__ == '__main__':
#     app.run(debug=True)
