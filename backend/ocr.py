import torch
import numpy as np
import cv2
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import pytesseract
from PIL import Image
import gc

# 🔥 Stable CPU usage
device = "cpu"
torch.set_num_threads(2)

processor = None
model = None


# ---------- LOAD MODEL ----------
def load_model():
    global processor, model

    if model is None or processor is None:
        print("🔥 Loading TrOCR BASE model...")

        processor = TrOCRProcessor.from_pretrained(
            "microsoft/trocr-base-handwritten",
            use_fast=True
        )

        model = VisionEncoderDecoderModel.from_pretrained(
            "microsoft/trocr-base-handwritten",
            low_cpu_mem_usage=True
        ).to(device)

        model.eval()
        print("✅ Model loaded once")


# ---------- IMAGE PREP ----------
def prepare_for_trocr(img):
    img = img.convert("RGB")

    # 🔥 IMPORTANT: don't over-shrink
    img.thumbnail((768, 768))

    return img


# ---------- SPLIT IMAGE (BETTER THAN FULL PAGE) ----------
def split_image(image):
    w, h = image.size

    parts = [
        image.crop((0, 0, w, h // 2)),
        image.crop((0, h // 2, w, h))
    ]

    return parts


# ---------- FULL IMAGE TROCR ----------
def full_image_trocr(image):
    parts = split_image(image)
    results = []

    for part in parts:
        img = prepare_for_trocr(part)

        pixel_values = processor(
            images=img,
            return_tensors="pt"
        ).pixel_values.to(device)

        with torch.no_grad():
            ids = model.generate(
                pixel_values,
                max_new_tokens=80,
                num_beams=2
            )

        text = processor.batch_decode(ids, skip_special_tokens=True)[0]
        results.append(text)

    return " ".join(results)


# ---------- QUALITY CHECK ----------
def is_bad(text):
    if text is None:
        return True

    text = text.strip()

    if len(text) < 5:
        return True

    digit_ratio = sum(c.isdigit() for c in text) / max(len(text), 1)

    if digit_ratio > 0.6:
        return True

    return False


# ---------- LINE DETECTION (FALLBACK ONLY) ----------
def extract_lines(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 10
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(15, image.width // 40), 3)
    )

    dilated = cv2.dilate(thresh, kernel, iterations=1)

    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    lines = []
    area_img = image.width * image.height

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        if (
            w * h > area_img * 0.001 and
            w > 30 and h > 10
        ):
            lines.append((x, y, w, h))

    return sorted(lines, key=lambda x: x[1])


# ---------- CROP ----------
def crop_lines(image, lines):
    crops = []

    for (x, y, w, h) in lines:
        pad = 5

        crops.append(
            image.crop((
                max(0, x - pad),
                max(0, y - pad),
                min(image.width, x + w + pad),
                min(image.height, y + h + pad)
            ))
        )

    return crops[:8]


# ---------- SEGMENTED TROCR ----------
def trocr_on_lines(line_images):
    texts = []

    for img in line_images:
        try:
            img = prepare_for_trocr(img)

            pixel_values = processor(
                images=img,
                return_tensors="pt"
            ).pixel_values.to(device)

            with torch.no_grad():
                ids = model.generate(
                    pixel_values,
                    max_new_tokens=60,
                    num_beams=2
                )

            text = processor.batch_decode(ids, skip_special_tokens=True)[0]
            texts.append(text)

        except:
            pass

    gc.collect()
    return " ".join(texts)


# ---------- TESSERACT ----------
def fallback_tesseract(image):
    print("⚠️ Using Tesseract fallback")
    return pytesseract.image_to_string(image)


# ---------- MAIN OCR ----------
def perform_ocr(image):
    print("🔍 OCR Started")

    load_model()

    # STEP 1: FULL IMAGE OCR (PRIMARY)
    text = full_image_trocr(image)

    if not is_bad(text):
        return text

    print("⚠️ Full-image weak → trying segmentation")

    # STEP 2: SEGMENTATION FALLBACK
    lines = extract_lines(image)

    if len(lines) > 0:
        crops = crop_lines(image, lines)
        text = trocr_on_lines(crops)

        if not is_bad(text):
            return text

    # STEP 3: FINAL FALLBACK
    return fallback_tesseract(image)