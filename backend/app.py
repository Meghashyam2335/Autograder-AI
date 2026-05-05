import os
import torch
import numpy as np
from PIL import Image
import easyocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path

from Score import calculate_grade
from textprocessor import clean_text

# ---------- APP ----------
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DEVICE ----------
device = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_num_threads(2)

print(f"🔥 Running on: {device}")

# ---------- LOAD MODELS ----------
print("🔥 Loading models...")

reader = easyocr.Reader(['en'], gpu=(device == "cuda"))

processor = TrOCRProcessor.from_pretrained(
    "microsoft/trocr-base-handwritten",
    use_fast=True
)

model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-handwritten",
    low_cpu_mem_usage=True
).to(device)

model.eval()

print("✅ Models loaded")


# ---------- TROCR FULL IMAGE FALLBACK ----------
def full_image_trocr(image):
    pixel_values = processor(
        images=image,
        return_tensors="pt"
    ).pixel_values.to(device)

    with torch.no_grad():
        ids = model.generate(
            pixel_values,
            max_new_tokens=120,
            num_beams=2
        )

    return processor.batch_decode(ids, skip_special_tokens=True)[0]


# ---------- OCR CORE ----------
def perform_ocr(image):
    print("🔍 OCR Started")

    img_array = np.array(image.convert("RGB"))

    # STEP 1: DETECT BOXES (EasyOCR)
    results = reader.readtext(img_array)

    boxes = []

    for (bbox, text, prob) in results:
        if prob < 0.25:
            continue

        x_min = int(min(p[0] for p in bbox))
        y_min = int(min(p[1] for p in bbox))
        x_max = int(max(p[0] for p in bbox))
        y_max = int(max(p[1] for p in bbox))

        boxes.append((x_min, y_min, x_max, y_max))

    if len(boxes) == 0:
        print("⚠️ No boxes → full image fallback")
        return full_image_trocr(image)

    # STEP 2: GROUP INTO LINES
    lines = []

    for box in boxes:
        placed = False

        for line in lines:
            if abs(box[1] - line[0][1]) < 25:
                line.append(box)
                placed = True
                break

        if not placed:
            lines.append([box])

    # sort lines top → bottom
    lines.sort(key=lambda l: l[0][1])

    texts = []

    # STEP 3: LINE-LEVEL TROCR
    for line in lines:
        line.sort(key=lambda b: b[0])

        x1 = min(b[0] for b in line)
        y1 = min(b[1] for b in line)
        x2 = max(b[2] for b in line)
        y2 = max(b[3] for b in line)

        crop = image.crop((x1, y1, x2, y2))

        crop = crop.convert("RGB")
        crop.thumbnail((512, 512))

        pixel_values = processor(
            images=crop,
            return_tensors="pt"
        ).pixel_values.to(device)

        with torch.no_grad():
            ids = model.generate(
                pixel_values,
                max_new_tokens=80,
                num_beams=3
            )

        text = processor.batch_decode(ids, skip_special_tokens=True)[0]

        texts.append(text)

    return "\n".join(texts)


# ---------- ROUTES ----------
@app.route('/')
def home():
    return "🚀 Backend Running (EasyOCR + TrOCR Hybrid)"


@app.route('/upload', methods=['POST'])
def upload_file():
    print("\n=== NEW REQUEST ===")

    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        full_text = ""

        # ---------- PDF ----------
        if file.filename.lower().endswith('.pdf'):
            images = convert_from_path(filepath, dpi=150)

            for img in images[:3]:
                full_text += perform_ocr(img) + " "

        # ---------- IMAGE ----------
        else:
            img = Image.open(filepath).convert("RGB")
            full_text = perform_ocr(img)

        clean_student = clean_text(full_text)
        print("\n🧹 PREPROCESSED TEXT:\n", clean_student)

        # TEMP IDEAL ANSWER
        ideal_answer = "machine learning is used for prediction and analysis"
        clean_ideal = clean_text(ideal_answer)

        score = calculate_grade(clean_ideal, clean_student)

        return jsonify({
            "score": score,
            "extracted_text": clean_student
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)