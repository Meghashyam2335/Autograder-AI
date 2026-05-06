import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load trained ML model
model = pickle.load(open("scoring_model.pkl", "rb"))

# Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def keyword_score(student_answer, keywords):
    count = 0
    student_answer = student_answer.lower()

    for kw in keywords:
        if kw.lower() in student_answer:
            count += 1

    coverage = count / len(keywords) if len(keywords) > 0 else 0
    return count, coverage


def calculate_grade(model_ans, student_ans, keywords):
    if not student_ans.strip():
        return 0.0

    emb_model = embed_model.encode(model_ans)
    emb_student = embed_model.encode(student_ans)

    sim = cosine_similarity(emb_model, emb_student)
    dot_product = np.dot(emb_model, emb_student)
    l2_dist = np.linalg.norm(emb_model - emb_student)
    semantic_gap = 1 - sim

    kw_count, kw_coverage = keyword_score(student_ans, keywords)
    kw_density = kw_coverage * (len(student_ans.split()) / len(model_ans.split()))
    kw_miss = len(keywords) - kw_count

    len_model = len(model_ans.split())
    len_student = len(student_ans.split())

    length_ratio = len_student / len_model if len_model > 0 else 0
    length_diff_norm = abs(len_student - len_model) / len_model if len_model > 0 else 0

    set1 = set(model_ans.lower().split())
    set2 = set(student_ans.lower().split())

    overlap = len(set1 & set2) / len(set1) if len(set1) > 0 else 0
    jaccard = len(set1 & set2) / len(set1 | set2) if len(set1 | set2) > 0 else 0
    overlap_student = len(set1 & set2) / len(set2) if len(set2) > 0 else 0

    sim_kw = sim * kw_coverage

    features = np.array([[
        sim, dot_product, l2_dist, semantic_gap,
        kw_coverage, kw_count, kw_density, kw_miss,
        length_ratio, length_diff_norm,
        overlap, jaccard, overlap_student,
        sim_kw
    ]])

    score = model.predict(features)[0]

    # Convert to percentage (optional)
    score = max(0.0, min(10.0, score))  # if model trained on 0–5

    return round(score, 2)