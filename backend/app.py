from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
import shutil
import os

# --- Import your custom functions here ---
# Replace 'extract_text', 'clean_text', and 'process_texts' 
# with the actual function names you created in these files.
from teseract import extract_text 
from Preprocessing import clean_text 
from textprocessor import process_texts 

app = FastAPI(title="Answer Evaluation API")

@app.post("/evaluate/")
async def evaluate_answer(
    ideal_answer: str = Form(...),
    written_answer_image: UploadFile = File(...)
):
    """
    Endpoint to evaluate a written answer image against an ideal text answer.
    """
    temp_file_path = f"temp_{written_answer_image.filename}"
    
    try:
        # Step 1: Save the uploaded image temporarily 
        # (Assuming your teseract function reads from a file path)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(written_answer_image.file, buffer)

        # Step 2: Use teseract.py to get text from the image
        extracted_written_text = extract_text(temp_file_path)

        # Step 3: Use Preprocessing.py to clean both texts
        cleaned_ideal = clean_text(ideal_answer)
        cleaned_written = clean_text(extracted_written_text)

        # Step 4: Use textprocessor.py to compare/process the answers
        final_result = process_texts(cleaned_ideal, cleaned_written)

        return {
            "status": "success",
            "extracted_text": extracted_written_text,
            "evaluation": final_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up the temporary image file after processing
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Optional: To run the file directly via python main.py
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

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

    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename
    })

# Run server
if __name__ == '__main__':
    app.run(debug=True)