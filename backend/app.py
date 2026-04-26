import os
import pytesseract
from Score import calculate_grade
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from pdf2image import convert_from_path

from Preprocessing import preprocess_image

from textprocessor import clean_text

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
        images = convert_from_path(
            filepath,
            poppler_path=r'C:\Users\msban\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin'
        )

        for img in images:
            processed = preprocess_image(img)

            text = pytesseract.image_to_string(
                processed,
                config='--oem 3 --psm 6'
            )

            extracted_text += text

    else:
        # If image
        img = Image.open(filepath)
        processed = preprocess_image(img)

        extracted_text = pytesseract.image_to_string(
            processed,
            config='--oem 3 --psm 6'
        )
    clean_student = clean_text(extracted_text)

    ideal_answer = """Photosynthesis is the essential biological process where plants, algae, and certain bacteria convert light energy into chemical energy to create food. Using chlorophyll, they transform carbon dioxide and water into glucose (sugar) and oxygen in the presence of sunlight, serving as the foundation for most life on Earth. 
How Photosynthesis Works
Ingredients: Plants require light, water and carbon dioxide
The Process: Chlorophyll (a green pigment in chloroplasts) captures light energy. This energy splits water molecules and converts into chemical energy, primarily in the form of glucose.
Location: The process primarily occurs in the leaves.
Outputs: The plant produces glucose for food/growth and releases oxygen as a waste product."""

    clean_ideal = clean_text(ideal_answer)

    score = calculate_grade(clean_ideal, clean_student)

    return jsonify({
        "message": "File uploaded and processed",
        "filename": file.filename,
        "extracted_text": extracted_text[:500],
        "score": score
    })


# Run server
if __name__ == '__main__':
    app.run(debug=True)