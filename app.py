from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
import pytesseract
import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

app = Flask(__name__)

GOOGLE_API_KEY= 'AIzaSyA95IplUbXmblGL_nrEv4dXR69zNY7bhnE'

genai.configure(api_key=GOOGLE_API_KEY)
# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def extract_text_from_image(image):
    # Preprocessing the image starts
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    extracted_text = ""
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = image[y:y + h, x:x + w]
        text = pytesseract.image_to_string(cropped)
        extracted_text += text + "\n"
    return extracted_text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If no file is selected
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Read the image file
            image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            # Extract text from the image
            extracted_text = extract_text_from_image(image)
            # Redirect to the result page with the extracted text
            return redirect(url_for('result', extracted_text=extracted_text))
    return render_template('index.html')
def to_string(text):
    text = text.replace('•', '*')
    text = text.replace('*', '')
    return textwrap.indent(text, '', predicate=lambda _: True)
@app.route('/result')
def result():
    extracted_text = request.args.get('extracted_text', '')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(extracted_text)
    response_text = response.text
    formatted_text = to_string(response_text)
    return render_template('result.html', extracted_text=formatted_text)
if __name__ == '__main__':
    app.run(debug=True)
