from flask import Flask
from flask_cors import CORS
from pathlib import Path
from typing import Union, Literal, List
from PyPDF2 import PdfWriter, PdfReader, Transformation
from PyPDF2.generic import AnnotationBuilder
from flask_restful import Resource, Api
from fpdf import FPDF
from flaskwebgui import FlaskUI  # import FlaskUI

import os
import signal
import sys
import requests
import random
import string
import io
import math
import json
import pypdfium2 as pdfium
import zipfile
import shutil
from threading import Timer
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file, jsonify
from werkzeug.utils import secure_filename
from os.path import join

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}},
            expose_headers=["Content-Disposition"])
app.config['CORS_HEADERS'] = 'application/json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    password: str,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    writer = PdfWriter()

    # reader = PdfReader(content_pdf)
    if(password):
        reader1 = PdfReader(content_pdf, False, password)
    else:
        reader1 = PdfReader(content_pdf)

    pdf_writer = PdfWriter()
    # pdf_writer.add_blank_page(
    #     reader1.pages[0].mediabox.width, reader1.pages[0].mediabox.height)
    # # Create the annotation and add it
    # annotation = AnnotationBuilder.free_text(
    #     "CONFIDENTIAL",
    #     rect=reader1.pages[0].mediabox,
    #     font="Calibri",
    #     bold=True,
    #     italic=True,
    #     font_size="100pt",
    #     font_color="cccccc",
    #     border_color="cccccc",
    #     background_color="cdcdcd",
    # )
    # pdf_writer.add_annotation(page_number=0, annotation=annotation)
    # # Write the annotated file to disk
    # with open("annotated-pdf.pdf", "wb") as fp:
    #     pdf_writer.write(fp)

    # reader = PdfReader(stamp_pdf)

    # for page in reader.pages:
    #     page.scale_to(reader1.pages[0].mediabox.width, reader1.pages[0].mediabox.height)
    #     pdf_writer.add_page(page)

    # letters = string.ascii_letters
    # tempfile = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
    # with open(join(app.config['UPLOAD_FOLDER'], tempfile), "wb") as fp:
    #     pdf_writer.write(fp)

    reader2 = PdfReader(stamp_pdf)
    image_page = reader2.pages[0]

    # os.unlink(join(app.config['UPLOAD_FOLDER'], tempfile))

    if page_indices == "ALL":
        page_indices = list(range(0, len(reader1.pages)))
    for index in page_indices:
        content_page = reader1.pages[index]
        mediabox = content_page.mediabox
        content_page.merge_page(image_page)
        content_page.mediabox = mediabox
        writer.add_page(content_page)
        # # Create the annotation and add it
        # annotation = AnnotationBuilder.free_text(
        #     "Hello World\nThis is the second line!",
        #     rect=mediabox,
        #     font="Arial",
        #     bold=True,
        #     italic=True,
        #     font_size="20pt",
        #     font_color="00ff00",
        #     border_color="0000ff",
        #     background_color="cdcdcd",
        # )
        # writer.add_annotation(page_number=0, annotation=annotation)

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


# @app.route('/watermark-pdf', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             originfile = join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(originfile)
#             # os.chmod(join('.', app.config['UPLOAD_FOLDER'], filename), 0o0777)
#             # os.chmod(join(app.config['UPLOAD_FOLDER']), 0o0777)

#             template = request.form.get('template')
#             password = request.form.get('password')
#             pdf_result = "pdf_result_" + template  # pdf_result_w1.pdf

#             stamp(originfile, join('files', template),
#                   join(UPLOAD_FOLDER, pdf_result), password)
#             return send_file(join('..', UPLOAD_FOLDER, pdf_result), mimetype='application/pdf')
#             # return redirect(url_for('download_file', name=filename))
#     return render_template('upload.html')


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
    stamp(join(app.config['UPLOAD_FOLDER'], tempfile), join('files', "w2.pdf"),
          join(UPLOAD_FOLDER, pdf_result), "")

    os.unlink(join(app.config['UPLOAD_FOLDER'], tempfile))

    return_data = io.BytesIO()
    with open(join(UPLOAD_FOLDER, pdf_result), 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(join(UPLOAD_FOLDER, pdf_result))

    return send_file(return_data, mimetype='application/pdf', attachment_filename=pdf_result, as_attachment=False, download_name=pdf_result)

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


# @app.route('/about')
# def about():
#     return 'About'

def watermark_template2(mediabox, watermarktempfile, text):
    pdf = FPDF(unit='pt', format=[int(mediabox.width), int(mediabox.height)])
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    # pdf.text(x=60, y=60, txt="Some text.")
    pdf.set_text_color(238, 238, 238)
    # pdf.cell(mediabox.width/100*60, mediabox.height, text, 0, ln=0, center=True)

    # pdf.cell(mediabox.width + 300, mediabox.height*1.6, text, center=True, align='R')
    # pdf.cell(mediabox.width/100*60, mediabox.height*1.6, text, center=True)

    if(mediabox.width < mediabox.height):
        pdf.rotate(45)
        # top
        pdf.cell(float(mediabox.width*95/100),
                 100, text, center=True, align='L')
        pdf.cell(float(mediabox.width*95/100), 100,
                 text, center=True, align='R', ln=0)

        pdf.cell(float(mediabox.width*230/100),
                 float(mediabox.height*60/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*130/100),
                 float(mediabox.height*60/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*30/100),
                 float(mediabox.height*60/100), text, center=True)
        pdf.cell(float(mediabox.width*130/100),
                 float(mediabox.height*60/100), text, center=True, align='R')

        # # center bottom
        pdf.cell(float(mediabox.width*290/100),
                 float(mediabox.height*110/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*180/100),
                 float(mediabox.height*110/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*80/100),
                 float(mediabox.height*110/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*95/100),
                 float(mediabox.height*110/100), text, center=True, align='R')

        # # bottom center
        pdf.cell(float(mediabox.width*130/100),
                 float(mediabox.height*160/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*250/100),
                 float(mediabox.height*160/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*30/100),
                 float(mediabox.height*160/100), text, center=True)
        pdf.cell(float(mediabox.width*130/100),
                 float(mediabox.height*160/100), text, center=True, align='R')

        pdf.cell(float(mediabox.width*180/100),
                 float(mediabox.height*220/100), text, center=True, align='L')
        # pdf.image("wm2.png", x=float(mediabox.width*30/100), y=-20, w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*30/100), y=float(mediabox.height*35/100), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*30/100), y=float(mediabox.height*80/100), w=250)

        # pdf.image("wm2.png", x=-120, y=-20, w=250)
        # pdf.image("wm2.png", x=-140, y=float(mediabox.height*33/100), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*85/100), y=float(mediabox.height*45/100), w=250)

        # pdf.image("wm2.png", x=float(mediabox.width/100*40), y=-40, w=250)
        # pdf.image("wm2.png", x=float(mediabox.width/100*20), y=float(mediabox.height/100*90), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width/100*90), y=float(mediabox.height/100*45), w=250)
        # pdf.image("wm2.png", x=-150, y=float(mediabox.height/100*35), w=250)
        # pdf.image("wm2.png", x=-150, y=-10, w=250)
    else:
        pdf.rotate(45)
        # top
        pdf.cell(float(mediabox.width*95/100),
                 100, text, center=True, align='L')
        pdf.cell(float(mediabox.width*95/100), 100,
                 text, center=True, align='R', ln=0)

        # pdf.cell(float(mediabox.width*230/100), float(mediabox.height*80/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*130/100),
                 float(mediabox.height*100/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*50/100),
                 float(mediabox.height*100/100), text, center=True, align='L')

        pdf.cell(float(mediabox.width*80/100),
                 float(mediabox.height*200/100), text, center=True, align='L')
        pdf.cell(float(mediabox.width*160/100),
                 float(mediabox.height*200/100), text, center=True, align='L')
        pdf.cell(20, float(mediabox.height*200/100),
                 text, center=True, align='L')
        pdf.cell(float(mediabox.width*45/100),
                 float(mediabox.height*300/100), text, center=True, align='L')
        # pdf.image("wm2.png", x=float(mediabox.width*40/100), y=-80, w=250)
        # pdf.image("wm2.png", x=0, y=float(mediabox.width*25/100), w=250)
        # pdf.image("wm2.png", x=-120, y=-20, w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*40/100), y=float(mediabox.width*33/100), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*85/100), y=float(mediabox.width*35/100), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width*85/100), y=float(-35), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width/100*30), y=-80, w=250)
        # pdf.image("wm2.png", x=float(mediabox.width/100*45), y=float(mediabox.height/100*80), w=250)
        # pdf.image("wm2.png", x=float(mediabox.width/100*85), y=float(mediabox.height/100*20), w=250)
        # pdf.image("wm2.png", x=-40, y=float(mediabox.height/100*40), w=250)
        # pdf.image("wm2.png", x=-20, y=float(-mediabox.height/100*25), w=250)

    # horizontal
    # if(mediabox.width > mediabox.height):
    #   pdf.image("wm2.png", x=mediabox.width/100*33, y=mediabox.height/100*50, w=250)
    # else:
    #   pdf.image("wm2.png", x=mediabox.width/100*30, y=mediabox.height/100*50, w=250)

    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))


def watermark_template3(mediabox, watermarktempfile, text):
    pdf = FPDF(unit='pt', format=[int(mediabox.width), int(mediabox.height)])
    pdf.add_page()
    pdf.set_font("Helvetica", size=48)
    # pdf.text(x=60, y=60, txt="Some text.")
    pdf.set_text_color(238, 238, 238)
    # pdf.cell(mediabox.width/100*60, mediabox.height, text, 0, ln=0, center=True)

    # pdf.cell(mediabox.width + 300, mediabox.height*1.6, text, center=True, align='R')
    # pdf.cell(mediabox.width/100*60, mediabox.height*1.6, text, center=True)
    if(mediabox.width > mediabox.height):
        pdf.rotate(45)
        pdf.cell(float(mediabox.width*100/100),
                 float(mediabox.height*180/100), text, center=True)
        # pdf.image("wm2.png", x=float(mediabox.width/100*33), y=float(mediabox.height/100*30), w=250)
    else:
        pdf.rotate(45)
        pdf.cell(float(mediabox.width*180/100),
                 float(mediabox.height*110/100), text, center=True)
        # pdf.image("wm2.png", x=float(mediabox.width/100*30), y=float(mediabox.height/100*30), w=250)

    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))

    # writer = PdfWriter()
    # readerwatermark = PdfReader(join(UPLOAD_FOLDER, watermarktempfile))
    # image_page = readerwatermark.pages[0]
    # image_page.add_transformation(Transformation().rotate(45))
    # # image_page.rotate(90)
    # writer.add_page(image_page)

    # with open(join(UPLOAD_FOLDER, watermarktempfile), "wb") as output_stream:
    #     writer.write(output_stream)


def watermark_template4(mediabox, watermarktempfile, text):
    pdf = FPDF(unit='pt', format=[int(mediabox.width), int(mediabox.height)])
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    # pdf.text(x=60, y=140, txt="Some text.")
    pdf.set_text_color(238, 238, 238)
    # top
    pdf.cell(float(mediabox.width*80/100), 100, text, center=True, align='L')
    pdf.cell(float(mediabox.width*95/100), 100,
             text, center=True, align='R', ln=0)

    pdf.cell(float(mediabox.width*130/100),
             float(mediabox.height*60/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*30/100),
             float(mediabox.height*60/100), text, center=True)
    pdf.cell(float(mediabox.width*130/100),
             float(mediabox.height*60/100), text, center=True, align='R')

    # # center bottom
    pdf.cell(float(mediabox.width*80/100),
             float(mediabox.height*110/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*95/100),
             float(mediabox.height*110/100), text, center=True, align='R')

    # # bottom center
    pdf.cell(float(mediabox.width*130/100),
             float(mediabox.height*160/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*30/100),
             float(mediabox.height*160/100), text, center=True)
    pdf.cell(float(mediabox.width*130/100),
             float(mediabox.height*160/100), text, center=True, align='R')
    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))


def watermark_template5(mediabox, watermarktempfile, text):
    pdf = FPDF(unit='pt', format=[int(mediabox.width), int(mediabox.height)])
    pdf.add_page()
    pdf.set_font("Helvetica", size=48)
    # pdf.text(x=60, y=140, txt="Some text.")
    pdf.set_text_color(238, 238, 238)
    # print(mediabox.height)
    if(mediabox.width < mediabox.height):
        pdf.cell(float(mediabox.width*55/100),
                 float(mediabox.height*90/100), text, center=True)
    else:
        pdf.cell(int(mediabox.width*40/100),
                 float(mediabox.height*90/100), text, center=True)
    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))


@app.route('/test-pdf', methods=['GET', 'POST'])
def test_pdf():
    url = request.args.get('url')
    r = requests.get(url)
    letters = string.ascii_letters
    tempfile = ''.join(random.choice(letters) for i in range(10)) + ".pdf"

    tmpdir = join('/tmp', tempfile)

    with open(tmpdir, 'wb') as f:
        f.write(r.content)
    return send_file(tmpdir, mimetype='application/pdf')


@app.route('/watermark-pdf', methods=['GET', 'POST'])
def watermark_pdf():
    url = request.args.get('url')
    template = int(request.args.get('template'))
    text = request.args.get('text')

    if not text:
        text = 'CONFIDENTIAL'

    r = requests.get(url)
    letters = string.ascii_letters
    tempfile = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
    watermarktempfile = ''.join(random.choice(letters)
                                for i in range(10)) + ".pdf"
    pdf_result = ''.join(random.choice(letters) for i in range(10)) + ".pdf"

    with open(join(app.config['UPLOAD_FOLDER'], tempfile), 'wb') as f:
        f.write(r.content)

    reader = PdfReader(join(app.config['UPLOAD_FOLDER'], tempfile))
    mediabox = reader.pages[0].mediabox

    # pdf_writer = PdfWriter()
    # pdf_writer.add_blank_page(mediabox.width, mediabox.height)
    # # Write the annotated file to disk
    # with open("watermark-template.pdf", "wb") as fp:
    #     pdf_writer.write(fp)
    if(template == 2):
        watermark_template2(mediabox, watermarktempfile, text)
    elif(template == 3):
        watermark_template3(mediabox, watermarktempfile, text)
    elif(template == 4):
        watermark_template4(mediabox, watermarktempfile, text)
    elif(template == 5):
        watermark_template5(mediabox, watermarktempfile, text)
    else:
        watermark_template5(mediabox, watermarktempfile, text)

    # os.unlink(join('..',app.config['UPLOAD_FOLDER'], watermarktempfile))

    # writer = PdfWriter()
    # writer.add_blank_page(width=mediabox.width, height=mediabox.height)

    # with open("output.pdf", "wb") as output_stream:
    #     writer.write(output_stream)

    # readerwatermark = PdfReader(join(UPLOAD_FOLDER, watermarktempfile))
    # content_page = reader.pages[0]
    # image_page = readerwatermark.pages[0]
    # image_page.add_transformation(Transformation().rotate(45))
    # image_page.rotate(90)
    # writer.add_page(image_page)

    # with open("output.pdf", "wb") as output_stream:
    #     writer.write(output_stream)

    # mediabox = content_page.mediabox
    # # content_page.add_transformation(Transformation().rotate(45))
    # content_page.merge_page(image_page)
    # content_page.mediabox = mediabox
    # writer.add_page(content_page)

    # with open("output.pdf", "wb") as output_stream:
    #     writer.write(output_stream)

    # return send_file(join('..', "output.pdf"), mimetype='application/pdf')
    # return send_file(join('..', UPLOAD_FOLDER, watermarktempfile), mimetype='application/pdf')

    watermark(join(app.config['UPLOAD_FOLDER'], tempfile), join(UPLOAD_FOLDER, watermarktempfile),
              join(UPLOAD_FOLDER, pdf_result), "")

    os.unlink(join(app.config['UPLOAD_FOLDER'], tempfile))
    os.unlink(join(app.config['UPLOAD_FOLDER'], watermarktempfile))

    return_data = io.BytesIO()
    with open(join(UPLOAD_FOLDER, pdf_result), 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(join(UPLOAD_FOLDER, pdf_result))

    return send_file(return_data, mimetype='application/pdf', attachment_filename=pdf_result, as_attachment=False, download_name=pdf_result)


def stamp2(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    password: str,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    if(password):
        stampreader = PdfReader(stamp_pdf, password=password)
        image_page = stampreader.pages[0]
    else:
        stampreader = PdfReader(stamp_pdf)
        image_page = stampreader.pages[0]

    writer = PdfWriter()

    contentreader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = list(range(0, len(contentreader.pages)))
    for index in page_indices:
        content_page = contentreader.pages[index]
        mediabox = content_page.mediabox
        # print('merge_page', mediabox)
        content_page.merge_page(image_page)
        content_page.mediabox = mediabox
        # Scale
        writer.add_page(content_page)

    with open(pdf_result, "wb") as fp:
        writer.write(fp)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


@app.route('/draw-template', methods=['POST'])
def draw_template():

    # default A4
    width = 210
    height = 297
    opacity = 0.25
    fontSize = 24
    text = 'CONFIDENTIAL'
    if request.files.get('file', None) != None:
        file = request.files['file']
        # file.seek(0, os.SEEK_END)
        filename = secure_filename(file.filename)
        originfile = join(app.config['UPLOAD_FOLDER'], filename)
        file.save(originfile)
        reader = PdfReader(originfile)
        mediabox = reader.pages[0].mediabox
        width = mediabox.width
        height = mediabox.height
        # convert string to  object
        data = json.loads(request.form['data'])
        viewport = json.loads(request.form['viewport'])
        textColor = json.loads(request.form['textColor'])
        containerRect = json.loads(request.form['containerRect'])
        opacity = float(request.form['opacity'])
        fontSize = float(request.form['fontSize'])
        text = str(request.form['text'])
        print('origin1', mediabox)
    else:
        # json
        # body = request.get_json()
        # data = body['data']
        # viewport = body['viewport']

        data = json.loads(request.form['data'])
        viewport = json.loads(request.form['viewport'])
        textColor = json.loads(request.form['textColor'])
        containerRect = json.loads(request.form['containerRect'])
        opacity = float(request.form['opacity'])
        fontSize = float(request.form['fontSize'])
        url = request.form['url']
        width = float(viewport['width'])
        height = float(viewport['height'])
        text = str(request.form['text'])

        r = requests.get(url)
        letters = string.ascii_letters
        filename = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
        originfile = join(app.config['UPLOAD_FOLDER'], filename)

        with open(originfile, 'wb') as f:
            f.write(r.content)

        reader = PdfReader(originfile)
        mediabox = reader.pages[0].mediabox
        print('origin2', mediabox)
        width = mediabox.width
        height = mediabox.height
        # width = containerRect['width']
        # height = containerRect['height']

    pdf = FPDF(unit='pt', format=[float(width), float(height)])
    pdf.add_page()
    pdf.add_font('Prompt', '', join('fonts', 'Prompt-Regular.ttf'), uni=True)
    pdf.set_font("Prompt", size=fontSize)
    # h = input('Enter hex: ').lstrip('#')
    # print('RGB =', tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
    if not textColor:
        pdf.set_text_color(255, 0, 0)
    else:
        pdf.set_text_color(textColor['r'], textColor['g'], textColor['b'])
    # pdf.set_fill_color(0, 255, 0)
    for item in data:
        origin_deg = float(item['origin_deg'])
        # print('origin_deg', origin_deg)
        # pdf.set_y(float(item['y']) + 100)
        # pdf.set_x(float(item['x']) + 100)

        if item['deg']:
            if(origin_deg <= 0 or origin_deg == 360):
                # print('deg[0,360]')
                pdf.rotate(float(item['deg']), float(
                    item['x']), float(item['y']) + 200)
            # 329-360
            if(origin_deg > 330 and origin_deg <= 360):
                # print('deg[330,360]')
                pdf.rotate(float(item['deg']), float(
                    item['x']), float(item['y']) + 40)
            # 330 - 265
            if(origin_deg > 265 and origin_deg <= 330):
                # print('deg[265,330]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 45)
            # 265 - 235
            if(origin_deg > 235 and origin_deg <= 265):
                # print('deg[235,265]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 46)
            # 235 - 115
            if(origin_deg > 115 and origin_deg <= 235):
                # print('deg[115,235]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 46)
            # 115 - 0
            if(origin_deg > 0 and origin_deg <= 115):
                # print('deg[0,115]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 3, float(item['y']) + 47)

        # pdf.set_xy(float(item['x']), float(item['y']))
        # pdf.rotation(float(item['deg']), float(item['x']), float(item['y']))
        with pdf.local_context(fill_opacity=opacity):
            # print('cell[width]', item['width'])
            # print('cell[height]', item['height'])
            pdf.text(float(item['x']) + 4, float(item['y']) + 30, text)
            # pdf.cell(float(item['width']), float(item['height']),
            #          text, 1, 0, align='L')
        # pdf.rect(float(item['x']), float(item['y']), float(item['width']), float(item['height']))
        # pdf.multi_cell(float(item['width']), float(item['height']),
        #          'CONFIDENTIAL')
        # pdf.text(float(item['x']), float(item['y']), 'CONFIDENTIAL')
        # pdf.set_x(0)
        # pdf.set_y(0)

    letters = string.ascii_letters
    watermarkfilename = ''.join(random.choice(letters)
                                for i in range(10)) + ".pdf"
    watermarkfile = join(app.config['UPLOAD_FOLDER'], watermarkfilename)
    # pdf.output('demo.pdf')

    pdf.output(watermarkfile)

    # return_data = io.BytesIO()
    # with open(watermarkfile, 'rb') as fo:
    #     return_data.write(fo.read())
    # # (after writing, cursor will be at last byte, so move it to start)
    # return_data.seek(0)
    # os.unlink(watermarkfile)
    # return send_file(return_data, mimetype='application/pdf', attachment_filename=watermarkfilename, as_attachment=True, download_name=watermarkfilename)

    letters = string.ascii_letters
    resultfilename = ''.join(random.choice(letters)
                             for i in range(10)) + ".pdf"
    resultfile = join(app.config['UPLOAD_FOLDER'], resultfilename)

    pdfpassword = ""

    stamp2(originfile, watermarkfile, resultfile, pdfpassword)

    # pdfimg = pdfium.PdfDocument(resultfile)
    # n_pages = len(pdfimg)  # get the number of pages in the document
    # page_indices = [i for i in range(n_pages)]  # all pages
    # renderer = pdfimg.render(
    #     pdfium.PdfBitmap.to_pil,
    #     page_indices=page_indices,
    #     scale=300/72,  # 300dpi resolution
    # )
    # # folder name
    # letters = string.ascii_letters
    # zipdirname = ''.join(random.choice(letters)
    #                      for i in range(10))
    # # folder path
    # zippath = join(app.config['UPLOAD_FOLDER'], zipdirname)
    # # create folder
    # if not os.path.exists(zippath):
    #     os.makedirs(zippath)
    # # export images
    # for i, image in zip(page_indices, renderer):
    #     image.save(join(zippath, "page_%0*d.jpg" % (1, i + 1)))
    # # zipfile name
    # zipfilename = zipdirname + ".zip"
    # with zipfile.ZipFile(join(app.config['UPLOAD_FOLDER'], zipfilename), 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     zipdir(zippath, zipf)
    # shutil.rmtree(zippath, ignore_errors=True)

    return_data = io.BytesIO()
    with open(resultfile, 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    # delete file
    os.unlink(originfile)
    os.unlink(watermarkfile)
    os.remove(resultfile)

    return send_file(return_data, mimetype='application/pdf', attachment_filename=resultfilename, as_attachment=True, download_name=resultfilename)
    # return jsonify(body)


@app.route('/pdf-to-image', methods=['POST'])
def pdf_to_image():

    # default A4
    width = 210
    height = 297
    opacity = 0.25
    fontSize = 24
    text = 'CONFIDENTIAL'
    if request.files.get('file', None) != None:
        file = request.files['file']
        # file.seek(0, os.SEEK_END)
        filename = secure_filename(file.filename)
        originfile = join(app.config['UPLOAD_FOLDER'], filename)
        file.save(originfile)
        reader = PdfReader(originfile)
        mediabox = reader.pages[0].mediabox
        width = mediabox.width
        height = mediabox.height
        # convert string to  object
        data = json.loads(request.form['data'])
        viewport = json.loads(request.form['viewport'])
        textColor = json.loads(request.form['textColor'])
        containerRect = json.loads(request.form['containerRect'])
        opacity = float(request.form['opacity'])
        fontSize = float(request.form['fontSize'])
        text = str(request.form['text'])
        print('origin1', mediabox)
    else:
        # json
        # body = request.get_json()
        # data = body['data']
        # viewport = body['viewport']

        data = json.loads(request.form['data'])
        viewport = json.loads(request.form['viewport'])
        textColor = json.loads(request.form['textColor'])
        containerRect = json.loads(request.form['containerRect'])
        opacity = float(request.form['opacity'])
        fontSize = float(request.form['fontSize'])
        url = request.form['url']
        width = float(viewport['width'])
        height = float(viewport['height'])
        text = str(request.form['text'])

        r = requests.get(url)
        letters = string.ascii_letters
        filename = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
        originfile = join(app.config['UPLOAD_FOLDER'], filename)

        with open(originfile, 'wb') as f:
            f.write(r.content)

        reader = PdfReader(originfile)
        mediabox = reader.pages[0].mediabox
        print('origin2', mediabox)
        width = mediabox.width
        height = mediabox.height
        # width = containerRect['width']
        # height = containerRect['height']

    pdf = FPDF(unit='pt', format=[float(width), float(height)])
    pdf.add_page()
    pdf.add_font('Prompt', '', join('fonts', 'Prompt-Regular.ttf'), uni=True)
    pdf.set_font("Prompt", size=fontSize)
    # h = input('Enter hex: ').lstrip('#')
    # print('RGB =', tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
    if not textColor:
        pdf.set_text_color(255, 0, 0)
    else:
        pdf.set_text_color(textColor['r'], textColor['g'], textColor['b'])
    # pdf.set_fill_color(0, 255, 0)
    for item in data:
        origin_deg = float(item['origin_deg'])
        # print('origin_deg', origin_deg)
        # pdf.set_y(float(item['y']) + 100)
        # pdf.set_x(float(item['x']) + 100)

        if item['deg']:
            if(origin_deg <= 0 or origin_deg == 360):
                # print('deg[0,360]')
                pdf.rotate(float(item['deg']), float(
                    item['x']), float(item['y']) + 200)
            # 329-360
            if(origin_deg > 330 and origin_deg <= 360):
                # print('deg[330,360]')
                pdf.rotate(float(item['deg']), float(
                    item['x']), float(item['y']) + 40)
            # 330 - 265
            if(origin_deg > 265 and origin_deg <= 330):
                # print('deg[265,330]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 45)
            # 265 - 235
            if(origin_deg > 235 and origin_deg <= 265):
                # print('deg[235,265]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 46)
            # 235 - 115
            if(origin_deg > 115 and origin_deg <= 235):
                # print('deg[115,235]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 2, float(item['y']) + 46)
            # 115 - 0
            if(origin_deg > 0 and origin_deg <= 115):
                # print('deg[0,115]')
                pdf.rotate(float(item['deg']), float(
                    item['x']) - 3, float(item['y']) + 47)

        # pdf.set_xy(float(item['x']), float(item['y']))
        # pdf.rotation(float(item['deg']), float(item['x']), float(item['y']))
        with pdf.local_context(fill_opacity=opacity):
            # print('cell[width]', item['width'])
            # print('cell[height]', item['height'])
            pdf.text(float(item['x']) + 4, float(item['y']) + 30, text)
            # pdf.cell(float(item['width']), float(item['height']),
            #          text, 1, 0, align='L')
        # pdf.rect(float(item['x']), float(item['y']), float(item['width']), float(item['height']))
        # pdf.multi_cell(float(item['width']), float(item['height']),
        #          'CONFIDENTIAL')
        # pdf.text(float(item['x']), float(item['y']), 'CONFIDENTIAL')
        # pdf.set_x(0)
        # pdf.set_y(0)

    letters = string.ascii_letters
    watermarkfilename = ''.join(random.choice(letters)
                                for i in range(10)) + ".pdf"
    watermarkfile = join(app.config['UPLOAD_FOLDER'], watermarkfilename)
    # pdf.output('demo.pdf')

    pdf.output(watermarkfile)

    # return_data = io.BytesIO()
    # with open(watermarkfile, 'rb') as fo:
    #     return_data.write(fo.read())
    # # (after writing, cursor will be at last byte, so move it to start)
    # return_data.seek(0)
    # os.unlink(watermarkfile)
    # return send_file(return_data, mimetype='application/pdf', attachment_filename=watermarkfilename, as_attachment=True, download_name=watermarkfilename)

    letters = string.ascii_letters
    resultfilename = ''.join(random.choice(letters)
                             for i in range(10)) + ".pdf"
    resultfile = join(app.config['UPLOAD_FOLDER'], resultfilename)

    pdfpassword = ""

    stamp2(originfile, watermarkfile, resultfile, pdfpassword)

    pdfimg = pdfium.PdfDocument(resultfile)
    n_pages = len(pdfimg)  # get the number of pages in the document
    page_indices = [i for i in range(n_pages)]  # all pages
    renderer = pdfimg.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=300/72,  # 300dpi resolution
    )
    # folder name
    letters = string.ascii_letters
    zipdirname = ''.join(random.choice(letters)
                         for i in range(10))
    # folder path
    zippath = join(app.config['UPLOAD_FOLDER'], zipdirname)
    # create folder
    if not os.path.exists(zippath):
        os.makedirs(zippath)
    # export images
    for i, image in zip(page_indices, renderer):
        image.save(join(zippath, "page_%0*d.jpg" % (2, i + 1)))
    # zipfile name
    zipfilename = zipdirname + ".zip"
    with zipfile.ZipFile(join(app.config['UPLOAD_FOLDER'], zipfilename), 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(zippath, zipf)
    shutil.rmtree(zippath, ignore_errors=True)

    return_data = io.BytesIO()
    with open(join(app.config['UPLOAD_FOLDER'], zipfilename), 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    # delete file
    os.unlink(originfile)
    os.unlink(watermarkfile)
    os.unlink(join(app.config['UPLOAD_FOLDER'], zipfilename))
    os.remove(resultfile)

    return send_file(return_data, mimetype='application/zip', attachment_filename=zipfilename, as_attachment=False, download_name=zipfilename)
    # return jsonify(body)


@app.route('/preview-demo', methods=['GET'])
def preview_demo():
    return send_file(join('..', UPLOAD_FOLDER, 'pdf_result2.pdf'), mimetype='application/pdf', attachment_filename='pdf_result2.pdf', as_attachment=False, download_name='pdf_result2.pdf')


if __name__ == '__main__':
    app.run(debug=True)
    # FlaskUI(app=app, server="flask", width=300, height=300).run()
# $ export FLASK_APP=./api/index.py
# $ export FLASK_ENV=development
# $ flask run
