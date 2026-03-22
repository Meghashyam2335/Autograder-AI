import cv2
import numpy as np
image_path = r"C:\Users\thris\Downloads\images.jpeg"
def preprocess_image(image_path):
    """
    Cleans an image to improve OCR accuracy.
    :param image_path: Path to the input image file.
    :return: Preprocessed image (numpy array).
    """
    # Load image
    image = cv2.imread(image_path)
        
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Remove Noise (Median Blur)
        # This helps with salt-and-pepper noise common in scans
    denoised = cv2.medianBlur(gray, 3)
        
        # 3. Thresholding (Binarization)
        # Otsu's thresholding automatically calculates the best threshold value
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('preprocessed_result.jpg', thresh)
    return thresh
