"""
CV preprocessing pipeline for food images.
Uses OpenCV and Pillow for image enhancement before AI analysis.
Reuses contour-based cropping technique from CVIP project.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode image bytes to OpenCV BGR array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def check_image_quality(img: np.ndarray) -> dict:
    """
    Assess image quality using Laplacian variance (blur detection).
    Returns quality metrics.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Brightness check
    brightness = np.mean(gray)

    return {
        "sharpness": float(laplacian_var),
        "brightness": float(brightness),
        "is_blurry": laplacian_var < 100,
        "is_too_dark": brightness < 50,
        "is_too_bright": brightness > 220,
        "resolution": f"{img.shape[1]}x{img.shape[0]}",
    }


def auto_crop_contour(img: np.ndarray) -> np.ndarray:
    """
    Auto-crop using contour detection (V-channel technique from CVIP project).
    Extracts the largest object region from the image.
    """
    # Convert to HSV and use V-channel
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]

    # Apply adaptive threshold
    blurred = cv2.GaussianBlur(v_channel, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return img

    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    area_ratio = cv2.contourArea(largest_contour) / (img.shape[0] * img.shape[1])

    # Only crop if the contour is meaningful (covers 5-90% of image)
    if 0.05 < area_ratio < 0.90:
        x, y, w, h = cv2.boundingRect(largest_contour)
        # Add padding (10%)
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
        x = max(0, x - pad_x)
        y = max(0, y - pad_y)
        w = min(img.shape[1] - x, w + 2 * pad_x)
        h = min(img.shape[0] - y, h + 2 * pad_y)
        img = img[y:y + h, x:x + w]

    return img


def white_balance(img: np.ndarray) -> np.ndarray:
    """Apply simple white balance correction using gray world assumption."""
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.mean(result[:, :, 1])
    avg_b = np.mean(result[:, :, 2])

    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)

    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)


def enhance_image(img: np.ndarray) -> np.ndarray:
    """Enhance image contrast and sharpness using Pillow."""
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # Auto contrast
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(1.2)

    # Sharpen slightly
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(1.3)

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def resize_optimal(img: np.ndarray, max_size: int = 1024) -> np.ndarray:
    """Resize image to optimal resolution for AI analysis while maintaining aspect ratio."""
    h, w = img.shape[:2]
    if max(h, w) <= max_size:
        return img

    scale = max_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def preprocess_food_image(image_bytes: bytes) -> tuple[bytes, dict]:
    """
    Full CV preprocessing pipeline for food images.
    Returns processed image bytes and quality metrics.

    Pipeline:
    1. Decode image
    2. Quality check (blur, brightness)
    3. White balance correction
    4. Auto-crop using contour detection
    5. Enhance contrast/sharpness
    6. Resize to optimal resolution
    7. Encode back to JPEG
    """
    # Decode
    img = decode_image(image_bytes)

    # Quality check on original
    quality = check_image_quality(img)
    logger.info(f"Image quality: {quality}")

    # White balance
    img = white_balance(img)

    # Auto-crop (contour-based from CVIP)
    img = auto_crop_contour(img)

    # Enhance
    img = enhance_image(img)

    # Resize
    img = resize_optimal(img, max_size=1024)

    # Encode to JPEG
    _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    processed_bytes = buffer.tobytes()

    quality["preprocessed"] = True
    quality["final_resolution"] = f"{img.shape[1]}x{img.shape[0]}"

    return processed_bytes, quality
