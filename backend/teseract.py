import google.generativeai as genai
from PIL import Image
import os

# 1. Configure your API key
# Replace "YOUR_API_KEY" with the key you got from Google AI Studio
genai.configure(api_key= "AIzaSyAeblcwzdGvX4I8fo7dfUPPq1G14hsXsoQ") 

# 2. Initialize the model 
# Gemini 1.5 Flash is extremely fast, free for standard use, and has incredible vision capabilities
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_and_split(image_path):
    """
    Sends an image directly to Gemini to extract text and format it into Q&A.
    """
    if not os.path.exists(image_path):
        return f"Error: Image not found at {image_path}"

    print(f"Uploading {os.path.basename(image_path)} to Gemini for processing...")
    
    # Load the raw image (No OpenCV preprocessing needed!)
    img = Image.open(image_path)

    # 3. The Prompt - This is where the magic happens
    prompt = """
    You are an extraction assistant. I am providing you with an image of a student answer sheet.
    
    TASK:
    1. Read the text from the image accurately. Ignore noise, page borders, and smudges.
    2. Analyze any diagrams drawn in the image and make a concise text description in two sentences inside the output String.
    3. Remove unwanted noise text such as Insitute Names, addresses, phone numbers, emails, e.t.c
    """

    try:
        # Pass both the prompt and the image to the model simultaneously
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"

# --- Test It Out ---
if __name__ == "__main__":
    # You can pass the ORIGINAL newspaper image here! No need for the preprocessed version.
    img_path = r"C:\Users\thris\Downloads\Autograder-AI\backend\preprocessed_result.jpg" 
    
    result = extract_and_split(img_path)
    
    print("\n--- Gemini Q&A Output ---")
    print(result)