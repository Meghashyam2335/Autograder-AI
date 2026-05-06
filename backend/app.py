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

exams = {}
submissions = {}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DEVICE ----------
device = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_num_threads(2)

print(f"🔥 Running on: {device}")

# ---------- LOAD MODELS ----------
print("🔥 Loading OCR models...")

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


import re

def extract_keywords(text):
    text = re.sub(r"[^a-zA-Z\s]", "", text.lower())

    stopwords = {
        "is","are","was","were","the","a","an","and","or",
        "of","to","in","for","with","on","by","uses","use"
    }

    words = text.split()

    return list(set([w for w in words if w not in stopwords and len(w) > 3]))


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

    img_array = np.array(image.convert("RGB"))
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
        return full_image_trocr(image)

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

    lines.sort(key=lambda l: l[0][1])

    texts = []

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

    return " ".join(texts)


# ---------- ROUTES ----------
@app.route('/')
def home():
    return "🚀 Backend Running (OCR + ML Ready)"


# ---------- UPLOAD ANSWER ----------
@app.route("/upload", methods=["POST"])
def upload():

    data = request.form

    student_id = data.get("student_id")
    exam_id = data.get("exam_id")
    question_id = data.get("question_id")

    if not student_id or not exam_id or not question_id:
        return jsonify({"error": "Missing fields"}), 400

    # CHECK KEY EXISTS
    exam_data = exams.get(exam_id, {}).get(question_id)

    if not exam_data:
        return jsonify({"error": "No answer key found"}), 400

    file = request.files["file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        full_text = ""

        # OCR PROCESSING
        if file.filename.lower().endswith(".pdf"):
            images = convert_from_path(filepath, dpi=150)
            for img in images[:3]:
                full_text += perform_ocr(img) + " "
        else:
            img = Image.open(filepath).convert("RGB")
            full_text = perform_ocr(img)

        # CLEAN STUDENT ANSWER
        student_text = clean_text(full_text)

        # FETCH STORED DATA
        ideal = exam_data["key"]
        keywords = exam_data["keywords"]

        # 🔥 FINAL ML SCORE (ONLY PLACE WHERE SCORING HAPPENS)
        score = calculate_grade(ideal, student_text, keywords)

        # FEEDBACK LOGIC (optional rule-based layer)
        if score >= 8:
            feedback = "Excellent answer"
        elif score >= 3:
            feedback = "Good but needs improvement"
        else:
            feedback = "Poor answer"

        # STORE RESULT
        if student_id not in submissions:
            submissions[student_id] = {}

        submissions[student_id][question_id] = {
            "exam_id": exam_id,
            "score": score,
            "feedback": feedback,
            "answer": student_text
        }

        return jsonify({
            "score": score,
            "feedback": feedback,
            "text": student_text
        })

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# ---------- UPLOAD KEY ----------
@app.route("/upload-key", methods=["POST"])
def upload_key():

    data = request.get_json()

    exam_id = data.get("exam_id")
    question_id = data.get("question_id")
    question = data.get("question")
    key = data.get("key")

    if not exam_id or not question_id or not question or not key:
        return jsonify({"error": "Missing fields"}), 400

    # CLEAN KEY
    cleaned_key = clean_text(key)

    # EXTRACT KEYWORDS (IMPORTANT FOR ML)
    keywords = extract_keywords(cleaned_key)

    if exam_id not in exams:
        exams[exam_id] = {}

    exams[exam_id][question_id] = {
        "question": question,
        "key": cleaned_key,
        "keywords": keywords   # 🔥 ADD THIS
    }

    return jsonify({"message": "Stored successfully"})


# ---------- GET QUESTIONS ----------
@app.route("/get-questions/<exam_id>", methods=["GET"])
def get_questions(exam_id):

    if exam_id not in exams:
        return jsonify({})

    return jsonify({
        qid: data["question"]
        for qid, data in exams[exam_id].items()
    })


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)