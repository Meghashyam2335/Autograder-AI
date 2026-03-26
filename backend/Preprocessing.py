import cv2
import numpy as np

def preprocess_image(image):
    """
    Accepts PIL image and processes it for OCR
    """

    # Convert PIL → OpenCV format
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 1. Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Noise removal
    denoised = cv2.medianBlur(gray, 3)

    # 3. Threshold
    _, thresh = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh
