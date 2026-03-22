import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import ssl

print("--- Script Started ---")

# --- 1. SSL Fix (Prevents silent hanging on Windows/Mac) ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- 2. Robust NLTK Downloads ---
print("Checking NLTK downloads (this might take 10-20 seconds the first time)...")
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)
print("NLTK data is ready!")

def clean_text(text):
    """
    Follows the 4-step flowchart to preprocess text for the Autograder.
    """
    if not isinstance(text, str):
        return ""

    # 1. Case Folding
    text_lower = text.lower()
    
    # 2. Tokenization (and removing punctuation)
    tokens = word_tokenize(text_lower)
    tokens = [word for word in tokens if word.isalnum()]
    
    # 3. Stopword Removal
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # 4. Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Join the tokens back into a single string
    cleaned_string = " ".join(lemmatized_tokens)
    
    return cleaned_string

# --- Test the Flowchart Logic ---
if __name__ == "__main__":
    print("\n--- Starting Text Processing ---")
    
    # Example data
    ideal_answer = "Photosynthesis is the process used by plants to convert light energy into chemical energy."
    student_answer = "Plants are using lights energy to converted it to chemicals energy."
    
    print("\n--- RAW DATA ---")
    print(f"Ideal: {ideal_answer}")
    print(f"Student: {student_answer}")
    
    print("\nProcessing Ideal Answer...")
    clean_ideal = clean_text(ideal_answer)
    
    print("Processing Student Answer...")
    clean_student = clean_text(student_answer)
    
    print("\n--- PREPROCESSED DATA (Output of Green Block) ---")
    print(f"Clean Ideal:   {clean_ideal}")
    print(f"Clean Student: {clean_student}")
    print("--- Script Finished Successfully ---")