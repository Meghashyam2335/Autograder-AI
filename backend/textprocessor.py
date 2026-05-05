import re
from spellchecker import SpellChecker

spell = SpellChecker()

# Common abbreviations / technical tokens to NEVER change
PROTECTED = {
    "ai", "ml", "api", "cpu", "gpu",
    "http", "https", "sql", "db",
    "os", "ui", "ux"
}


# ---------- STEP 1: REMOVE OCR NOISE ----------
def remove_noise(text):
    text = re.sub(r'[^a-zA-Z0-9\s.,?!]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ---------- STEP 2: REMOVE REPEATED WORDS ----------
def remove_repeated_words(text):
    words = text.split()
    cleaned = []

    for i, word in enumerate(words):
        if i > 0 and word.lower() == words[i - 1].lower():
            continue
        cleaned.append(word)

    return " ".join(cleaned)


# ---------- STEP 3: SAFE SPELL CORRECTION ----------
def correct_spelling(text):
    words = text.split()
    corrected = []

    # frequency map (to protect repeated meaningful words)
    word_freq = {}
    for w in words:
        w_lower = w.lower()
        word_freq[w_lower] = word_freq.get(w_lower, 0) + 1

    for word in words:
        w = word.lower()

        # protect known abbreviations
        if w in PROTECTED:
            corrected.append(word)
            continue

        # protect words repeated multiple times (likely valid)
        if word_freq[w] > 2:
            corrected.append(word)
            continue

        # skip very short words
        if len(word) <= 2:
            corrected.append(word)
            continue

        suggestion = spell.correction(word)

        if suggestion:
            # accept only small changes
            if abs(len(word) - len(suggestion)) <= 1:
                corrected.append(suggestion)
            else:
                corrected.append(word)
        else:
            corrected.append(word)

    return " ".join(corrected)


# ---------- STEP 4: SENTENCE CLEANUP ----------
def fix_sentence_structure(text):
    text = text.lower()

    # split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    cleaned = []

    for s in sentences:
        s = s.strip()

        if not s:
            continue

        # capitalize first letter
        s = s[0].upper() + s[1:]

        # ensure sentence ends properly
        if s[-1] not in ".!?":
            s += "."

        cleaned.append(s)

    return " ".join(cleaned)


# ---------- MAIN PIPELINE ----------
def clean_text(text):
    text = remove_noise(text)
    text = remove_repeated_words(text)
    text = correct_spelling(text)
    text = fix_sentence_structure(text)
    return text

