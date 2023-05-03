from flask import Flask
from flask_cors import CORS
from pathlib import Path
from typing import Union, Literal, List
from PyPDF2 import PdfWriter, PdfReader, Transformation
from PyPDF2.generic import AnnotationBuilder
from flask_restful import Resource, Api
from fpdf import FPDF

import os
import signal
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
CORS(app)
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
      pdf.cell(float(mediabox.width*95/100), 100, text, center=True, align='L')
      pdf.cell(float(mediabox.width*95/100), 100, text, center=True, align='R', ln=0)

      pdf.cell(float(mediabox.width*230/100), float(mediabox.height*60/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*130/100), float(mediabox.height*60/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*30/100), float(mediabox.height*60/100), text, center=True)
      pdf.cell(float(mediabox.width*130/100), float(mediabox.height*60/100), text, center=True, align='R')

      # # center bottom
      pdf.cell(float(mediabox.width*290/100), float(mediabox.height*110/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*180/100), float(mediabox.height*110/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*80/100), float(mediabox.height*110/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*95/100), float(mediabox.height*110/100), text, center=True, align='R')

      # # bottom center
      pdf.cell(float(mediabox.width*130/100), float(mediabox.height*160/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*250/100), float(mediabox.height*160/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*30/100), float(mediabox.height*160/100), text, center=True)
      pdf.cell(float(mediabox.width*130/100), float(mediabox.height*160/100), text, center=True, align='R')

      pdf.cell(float(mediabox.width*180/100), float(mediabox.height*220/100), text, center=True, align='L')
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
      pdf.cell(float(mediabox.width*95/100), 100, text, center=True, align='L')
      pdf.cell(float(mediabox.width*95/100), 100, text, center=True, align='R', ln=0)

      # pdf.cell(float(mediabox.width*230/100), float(mediabox.height*80/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*130/100), float(mediabox.height*100/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*50/100), float(mediabox.height*100/100), text, center=True, align='L')


      pdf.cell(float(mediabox.width*80/100), float(mediabox.height*200/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*160/100), float(mediabox.height*200/100), text, center=True, align='L')
      pdf.cell(20, float(mediabox.height*200/100), text, center=True, align='L')
      pdf.cell(float(mediabox.width*45/100), float(mediabox.height*300/100), text, center=True, align='L')
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
      pdf.cell(float(mediabox.width*100/100), float(mediabox.height*180/100), text, center=True)
      # pdf.image("wm2.png", x=float(mediabox.width/100*33), y=float(mediabox.height/100*30), w=250)
    else:
      pdf.rotate(45)
      pdf.cell(float(mediabox.width*180/100), float(mediabox.height*110/100), text, center=True)
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
    pdf.cell(float(mediabox.width*95/100), 100, text, center=True, align='R', ln=0)

    pdf.cell(float(mediabox.width*130/100), float(mediabox.height*60/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*30/100), float(mediabox.height*60/100), text, center=True)
    pdf.cell(float(mediabox.width*130/100), float(mediabox.height*60/100), text, center=True, align='R')

    # # center bottom
    pdf.cell(float(mediabox.width*80/100), float(mediabox.height*110/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*95/100), float(mediabox.height*110/100), text, center=True, align='R')

    # # bottom center
    pdf.cell(float(mediabox.width*130/100), float(mediabox.height*160/100), text, center=True, align='L')
    pdf.cell(float(mediabox.width*30/100), float(mediabox.height*160/100), text, center=True)
    pdf.cell(float(mediabox.width*130/100), float(mediabox.height*160/100), text, center=True, align='R')
    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))

def watermark_template5(mediabox, watermarktempfile, text):
    pdf = FPDF(unit='pt', format=[int(mediabox.width), int(mediabox.height)])
    pdf.add_page()
    pdf.set_font("Helvetica", size=48)
    # pdf.text(x=60, y=140, txt="Some text.")
    pdf.set_text_color(238, 238, 238)
    print(mediabox.height)
    if(mediabox.width < mediabox.height):
      pdf.cell(float(mediabox.width*55/100), float(mediabox.height*90/100), text, center=True)
    else:
      pdf.cell(int(mediabox.width*40/100), float(mediabox.height*90/100), text,center=True)
    pdf.output(join(UPLOAD_FOLDER, watermarktempfile))
    

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
    watermarktempfile = ''.join(random.choice(letters) for i in range(10)) + ".pdf"
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

    stamp(join(app.config['UPLOAD_FOLDER'], tempfile), join(UPLOAD_FOLDER, watermarktempfile),
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


if __name__ == '__main__':
    app.run(debug=True)
