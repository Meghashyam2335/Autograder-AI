from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_grade(clean_ideal_answer, clean_student_answer):
    if not clean_student_answer.strip():
        return 0.0

    ideal_embedding = model.encode(clean_ideal_answer, convert_to_tensor=True)
    student_embedding = model.encode(clean_student_answer, convert_to_tensor=True)

    cosine_score = util.cos_sim(ideal_embedding, student_embedding).item()

    # Convert to percentage
    final_score = round(cosine_score * 100, 1)

    # Clamp between 0 and 100
    final_score = max(0.0, min(100.0, final_score))

    return final_score