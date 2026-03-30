import cv2
import numpy as np
from PIL import Image
from io import BytesIO


def preprocess_food_image(image_bytes: bytes) -> bytes:
    """CV preprocessing pipeline for food images before AI analysis."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return image_bytes

    # 1. Auto white balance (gray world assumption)
    img = auto_white_balance(img)

    # 2. Resize to optimal size for AI (max 1024px, preserve aspect ratio)
    img = resize_optimal(img, max_dim=1024)

    # 3. Blur detection — warn if too blurry
    blur_score = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    if blur_score < 50:
        # Sharpen slightly if blurry
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)

    # 4. Enhance contrast using CLAHE on L channel
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # 5. Auto crop to food region using contour detection
    img = auto_crop_food(img)

    # Encode back to JPEG
    _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return buffer.tobytes()


def auto_white_balance(img: np.ndarray) -> np.ndarray:
    """Gray world white balance correction."""
    result = img.copy().astype(np.float32)
    avg_b, avg_g, avg_r = np.mean(result, axis=(0, 1))
    avg_all = (avg_b + avg_g + avg_r) / 3
    result[:, :, 0] *= avg_all / max(avg_b, 1)
    result[:, :, 1] *= avg_all / max(avg_g, 1)
    result[:, :, 2] *= avg_all / max(avg_r, 1)
    return np.clip(result, 0, 255).astype(np.uint8)


def resize_optimal(img: np.ndarray, max_dim: int = 1024) -> np.ndarray:
    """Resize keeping aspect ratio, only if larger than max_dim."""
    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return img
    scale = max_dim / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def auto_crop_food(img: np.ndarray) -> np.ndarray:
    """Try to crop to the main food region using contour detection."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return img

    # Get the bounding box of all significant contours
    h, w = img.shape[:2]
    min_area = h * w * 0.05  # ignore contours smaller than 5% of image

    significant = [c for c in contours if cv2.contourArea(c) > min_area]
    if not significant:
        return img

    # Union bounding box of all significant contours
    all_points = np.vstack(significant)
    x, y, cw, ch = cv2.boundingRect(all_points)

    # Add 5% padding
    pad_x, pad_y = int(cw * 0.05), int(ch * 0.05)
    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(w, x + cw + pad_x)
    y2 = min(h, y + ch + pad_y)

    # Only crop if it's meaningfully different from the original
    crop_area = (x2 - x1) * (y2 - y1)
    if crop_area < h * w * 0.3:
        return img  # crop too small, likely incorrect detection

    return img[y1:y2, x1:x2]
