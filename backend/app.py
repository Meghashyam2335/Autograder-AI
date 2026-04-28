import os
import torch
from PIL import Image
import easyocr
import numpy as np
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path

# Custom imports
from Score import calculate_grade
from textprocessor import clean_text

app = Flask(__name__)
CORS(app)

# --- Initialize TrOCR and EasyOCR once ---
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading models on {device}...")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten").to(device)
reader = easyocr.Reader(['en'], gpu=(device == "cuda")) # Tell EasyOCR to use GPU if available

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def perform_trocr_ocr(image):
    """
    Detects text regions using EasyOCR and transcribes them using TrOCR.
    """
    img_array = np.array(image.convert("RGB"))
    
    # 1. Detect text boxes
    results = reader.readtext(img_array) 
    extracted_segments = []

    # 2. Sort results by vertical position (Y-coordinate) to maintain readability
    results.sort(key=lambda x: x[0][0][1])

    for (bbox, text, prob) in results:
        # 3. Safely cast coordinates to integers for PIL
        top_left = bbox[0]
        bottom_right = bbox[2]
        
        left = int(top_left[0])
        upper = int(top_left[1])
        right = int(bottom_right[0])
        lower = int(bottom_right[1])
        
        # Crop the line from the original PIL image
        line_crop = image.crop((left, upper, right, lower))

        # 4. Transcribe with TrOCR
        pixel_values = processor(images=line_crop, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values, max_new_tokens=64)
        clean_segment = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        extracted_segments.append(clean_segment)

    # Join and clean punctuation
    raw_text = " ".join(extracted_segments)
    return raw_text.replace(" .", ".").replace(" ,", ",").strip()

@app.route('/')
def home():
    return "AutoGrader Backend with TrOCR Running"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    full_extracted_text = ""

    try:
        # Handle PDF or Image
        if file.filename.lower().endswith('.pdf'):
            # Note: Ensure poppler is in your system PATH
            images = convert_from_path(filepath)
            for img in images:
                text = perform_trocr_ocr(img)
                full_extracted_text += text + " "
        else:
            img = Image.open(filepath).convert("RGB")
            full_extracted_text = perform_trocr_ocr(img)

        clean_student = clean_text(full_extracted_text)
        
        # Placeholder for ideal answer logic
        ideal_answer = "" 
        clean_ideal = clean_text(ideal_answer)

        score = calculate_grade(clean_ideal, clean_student)

        # Cleanup: Delete the file after successful processing
        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({
            "score": score,
            "extracted_text": clean_student 
        })

    except Exception as e:
        # Cleanup file if an error occurs during processing
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)