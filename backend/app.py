import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

app = Flask(__name__)
CORS(app)

# Folder to store uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route
@app.route('/')
def home():
    return "AutoGrader Backend Running"

# Upload UI (GET)
@app.route('/upload-page', methods=['GET'])
def upload_page():
    return '''
    <h2>Upload File</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit">
    </form>
    '''

# Upload API (POST)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    extracted_text = ""

    # If PDF → convert to images
    if file.filename.endswith('.pdf'):
        images = convert_from_path(filepath, poppler_path=r'C:\Users\msban\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin')

        for img in images:
            text = pytesseract.image_to_string(img)
            extracted_text += text

    else:
        # If image
        img = Image.open(filepath)
        extracted_text = pytesseract.image_to_string(img)

    return jsonify({
        "message": "File uploaded and processed",
        "filename": file.filename,
        "extracted_text": extracted_text[:500]  # limit output
    })

# Run server
if __name__ == '__main__':
    app.run(debug=True)