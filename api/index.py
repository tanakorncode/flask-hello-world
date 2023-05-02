from flask import Flask
from pathlib import Path
from typing import Union, Literal, List
from PyPDF2 import PdfWriter, PdfReader
from flask_restful import Resource, Api

import os, signal
import sys
import requests
import random
import string
import io
from threading import Timer
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
from os.path import join

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    password: str,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    if(password):
        reader = PdfReader(stamp_pdf, False, password)
    else:
        reader = PdfReader(stamp_pdf)
    # reader = PdfReader(stamp_pdf)
    image_page = reader.pages[0]

    writer = PdfWriter()

    # reader = PdfReader(content_pdf)
    if(password):
        reader = PdfReader(content_pdf, False, password)
    else:
        reader = PdfReader(content_pdf)

    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))
    for index in page_indices:
        content_page = reader.pages[index]
        mediabox = content_page.mediabox
        content_page.merge_page(image_page)
        content_page.mediabox = mediabox
        writer.add_page(content_page)

    with open(pdf_result, "wb") as fp:
        writer.write(fp)


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
    
    # output = open(pdf_result, "wb")
    # return writer.write(output)
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
            originfile = join(app.config['UPLOAD_FOLDER'], filename)
            file.save(originfile)
            # os.chmod(join('.', app.config['UPLOAD_FOLDER'], filename), 0o0777)
            # os.chmod(join(app.config['UPLOAD_FOLDER']), 0o0777)

            template = request.form.get('template')
            password = request.form.get('password')
            pdf_result = "pdf_result_" + template  # pdf_result_w1.pdf

            stamp(originfile, join('files', template),
                  join(UPLOAD_FOLDER, pdf_result), password)
            return send_file(join('..', UPLOAD_FOLDER, pdf_result), mimetype='application/pdf')
            # return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')

@app.route('/pdf-view', methods=['GET', 'POST'])
def preview_pdf():
    # if request.method == 'POST':
    # check if the post request has the file part
    # if 'file' not in request.files:
    #     flash('No file part')
    #     return redirect(request.url)
    # file = request.files['file']
    # # If the user does not select a file, the browser submits an
    # # empty file without a filename.
    # if file.filename == '':
    #     flash('No selected file')
    #     return redirect(request.url)
    # data = request.get_json()
    # print(data['url'])
    url = request.args.get('url')

    r = requests.get(url)
    letters = string.ascii_letters
    tempfile = ''.join(random.choice(letters) for i in range(10)) + ".pdf"

    with open(join(app.config['UPLOAD_FOLDER'], tempfile), 'wb') as f:
        f.write(r.content)

    pdf_result = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
    stamp(join(app.config['UPLOAD_FOLDER'], tempfile), join('files', "w1.pdf"),
          join(UPLOAD_FOLDER, pdf_result), "")
    
    os.unlink(join(app.config['UPLOAD_FOLDER'], tempfile))

    return_data = io.BytesIO()
    with open(join(UPLOAD_FOLDER, pdf_result), 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(join(UPLOAD_FOLDER, pdf_result))

    return send_file(return_data, mimetype='application/pdf')

    # return send_file(join('..', UPLOAD_FOLDER, pdf_result), mimetype='application/pdf')
    # return 'get!'

    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         originfile = join(app.config['UPLOAD_FOLDER'], filename)
    #         file.save(originfile)
    #         # os.chmod(join('.', app.config['UPLOAD_FOLDER'], filename), 0o0777)
    #         # os.chmod(join(app.config['UPLOAD_FOLDER']), 0o0777)

    #         template = request.form.get('template')
    #         password = request.form.get('password')
    #         pdf_result = "pdf_result_" + template  # pdf_result_w1.pdf

    #         watermark(originfile, join('files', template),
    #                   join(UPLOAD_FOLDER, pdf_result), password)
    #         return send_file(join('..', UPLOAD_FOLDER, pdf_result), mimetype='application/pdf')
    #         # return redirect(url_for('download_file', name=filename))
    # return render_template('upload.html')


@app.route('/about')
def about():
    return 'About'


if __name__ == '__main__':
    app.run(debug=True)
