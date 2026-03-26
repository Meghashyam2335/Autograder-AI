import os
import cv2
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Import your custom modules
from Preprocessing import preprocess_image
from teseract import extract_and_split
from textprocessor import clean_text
from score import calculate_grade

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_pipeline(image_file):
    """
    Helper function to run the full pipeline:
    Save -> Preprocess -> Gemini OCR -> NLTK Cleaning
    """
    # 1. Save original
    filename = secure_filename(image_file.filename)
    raw_path = os.path.join(UPLOAD_FOLDER, f"raw_{filename}")
    image_file.save(raw_path)

    # 2. Preprocessing (OpenCV)
    # Your script saves 'preprocessed_result.jpg' by default; 
    # we'll capture the returned array and save a specific copy for Gemini
    processed_array = preprocess_image(raw_path)
    proc_path = os.path.join(UPLOAD_FOLDER, f"proc_{filename}")
    cv2.imwrite(proc_path, processed_array)

    # 3. Extraction (Gemini)
    extracted_text = extract_and_split(proc_path)

    # 4. Text Cleaning (NLTK)
    cleaned_text = clean_text(extracted_text)

    # Cleanup temp files
    if os.path.exists(raw_path): os.remove(raw_path)
    if os.path.exists(proc_path): os.remove(proc_path)

    return extracted_text, cleaned_text

@app.route('/grade_images', methods=['POST'])
def grade_images():
    # Check if both images are in the request
    if 'student_image' not in request.files or 'ideal_image' not in request.files:
        return jsonify({"error": "Please upload both student_image and ideal_image"}), 400

    try:
        # Process Student Answer
        raw_student, clean_student = process_pipeline(request.files['student_image'])

        # Process Ideal Answer
        raw_ideal, clean_ideal = process_pipeline(request.files['ideal_image'])

        # Final Scoring (Sentence Transformers)
        final_score = calculate_grade(clean_ideal, clean_student)

        return jsonify({
            "status": "success",
            "student": {
                "extracted": raw_student,
                "cleaned": clean_student
            },
            "ideal": {
                "extracted": raw_ideal,
                "cleaned": clean_ideal
            },
            "score": final_score,
            "max_score": 10.0
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Using threaded=True because Gemini API and Sentence Transformers 
    # can be heavy on resources
    app.run(debug=True, port=5000, threaded=True)