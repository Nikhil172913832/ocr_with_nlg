from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'statics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'

    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        extracted_text = extract_text(image_path)
        return render_template('index.html', extracted_text=extracted_text)

def extract_text(image_path):
    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

if __name__ == '__main__':
    app.run(debug=True)
