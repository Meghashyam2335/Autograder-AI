from sentence_transformers import SentenceTransformer, util

# print("Loading Local Scoring Model (MiniLM)...")
# 'all-MiniLM-L6-v2' is highly optimized. It's fast, small (~80MB), and incredibly accurate.
# It will download automatically the first time you run this.
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_grade(clean_ideal_answer, clean_student_answer):
    """
    Converts text to Sentence Embeddings and calculates the Cosine Similarity score.
    """
    # If the student wrote nothing, immediate zero.
    if not clean_student_answer.strip():
        return 0.0

    # print("Generating sentence embeddings...")
    # 1. Convert the text into mathematical vectors
    ideal_embedding = model.encode(clean_ideal_answer, convert_to_tensor=True)
    student_embedding = model.encode(clean_student_answer, convert_to_tensor=True)

    # 2. Similarity Check (Cosine Similarity)
    # This outputs a decimal between -1 and 1. (1 means completely identical meaning)
    cosine_score = util.cos_sim(ideal_embedding, student_embedding).item()

    # 3. Evaluation and Scoring (Convert to Percentage)
    # Multiply by 100 and round to 2 decimal places
    final_score = round(cosine_score * 10, 1)
    
    # Ensure the score doesn't go below 0 (sometimes completely unrelated vectors yield tiny negative numbers)
    final_score = max(0.0, final_score)

    return final_score

# --- Test the Scoring Engine ---
if __name__ == "__main__":
    print("\n--- Testing Autograder Similarity Check ---")
    
    # Let's test it with your preprocessed outputs
    # Notice how the student uses different words, but the SAME concept
    clean_ideal = "photosynthesis process plant convert light energy chemical energy"
    
    # Scenario A: Good Answer (Uses synonyms)
    clean_student_good = "plant use sunlight turn chemical power"
    
    # Scenario B: Bad Answer (Completely wrong concept)
    clean_student_bad = "mitochondria powerhouse cell produce atp"
    
    # Calculate Scores
    score_good = calculate_grade(clean_ideal, clean_student_good)
    score_bad = calculate_grade(clean_ideal, clean_student_bad)
    
    print("\n--- RESULTS ---")
    print(f"Ideal Answer Vector: '{clean_ideal}'\n")
    
    print(f"Student A Vector: '{clean_student_good}'")
    print(f"Student A Score:  {score_good}/100\n")
    
    print(f"Student B Vector: '{clean_student_bad}'")
    print(f"Student B Score:  {score_bad}/100")