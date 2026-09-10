"""
biometrics.py - Biometric Vision & Face Match Engine
Computes real-time similarity and confidence percentages between an enrolled
reference photo and a live IoT camera capture using PIL and NumPy.
"""

import io
import math
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageOps, ImageFilter
import numpy as np


def load_image_bytes(image_data: bytes) -> Optional[Image.Image]:
    """Safely loads bytes into a PIL RGB image with proper EXIF orientation handling."""
    try:
        img = Image.open(io.BytesIO(image_data))
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img
    except Exception:
        return None


def rotate_image(image_data: bytes, rotation_degrees: int = 90) -> bytes:
    """
    Rotates image by 0, 90, 180, or 270 degrees.
    90 degrees rotates counter-clockwise (positioning sideways phone streams upright).
    """
    if rotation_degrees == 0:
        return image_data
    img = load_image_bytes(image_data)
    if img is None:
        return image_data
    if rotation_degrees == 90:
        img = img.transpose(Image.Transpose.ROTATE_90)
    elif rotation_degrees == 180:
        img = img.transpose(Image.Transpose.ROTATE_180)
    elif rotation_degrees == 270:
        img = img.transpose(Image.Transpose.ROTATE_270)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def crop_to_portrait(image_data: bytes, aspect_ratio: float = 0.75) -> bytes:
    """
    Ensures captured frame is in vertical portrait orientation (3:4 aspect ratio)
    matching the registered official ID card photo.
    If image is wider than tall (landscape), crops the sides centered on the subject.
    """
    img = load_image_bytes(image_data)
    if img is None:
        return image_data

    w, h = img.size
    if w > h:
        target_w = int(h * aspect_ratio)
        if target_w < w:
            left = (w - target_w) // 2
            img = img.crop((left, 0, left + target_w, h))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def generate_default_avatar(name: str = "Yuvasri Eswara") -> bytes:
    """
    Generates a clean, stylized high-resolution biometric reference avatar.
    Uses name hash to produce unique color palettes for each student.
    """
    import hashlib
    from PIL import ImageDraw

    width, height = 300, 300
    
    # Generate unique color themes based on name hash
    palettes = [
        {"bg": (30, 58, 138), "ring": (96, 165, 250), "skin": (224, 231, 255), "shirt": (147, 197, 253)},
        {"bg": (76, 29, 149), "ring": (192, 132, 252), "skin": (243, 232, 255), "shirt": (216, 180, 254)},
        {"bg": (6, 78, 59), "ring": (52, 211, 153), "skin": (209, 250, 229), "shirt": (110, 231, 183)},
        {"bg": (136, 19, 55), "ring": (251, 113, 133), "skin": (255, 228, 230), "shirt": (244, 63, 94)},
        {"bg": (120, 53, 15), "ring": (251, 191, 36), "skin": (254, 243, 199), "shirt": (245, 158, 11)},
    ]
    hash_idx = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16) % len(palettes)
    pal = palettes[hash_idx]

    img = Image.new("RGB", (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Outer decorative ring
    draw.ellipse([20, 20, 280, 280], outline=pal["ring"], width=4)

    # Head
    draw.ellipse([105, 60, 195, 155], fill=pal["skin"], outline=pal["ring"], width=2)
    # Eyes
    draw.ellipse([128, 95, 140, 107], fill=pal["bg"])
    draw.ellipse([160, 95, 172, 107], fill=pal["bg"])
    # Smile arc
    draw.arc([136, 115, 164, 133], start=0, end=180, fill=pal["bg"], width=2)

    # Torso / shoulders
    draw.chord([55, 165, 245, 320], start=180, end=0, fill=pal["shirt"])

    # Name initials badge
    initials = "".join([part[0] for part in name.split() if part])[:2].upper()
    draw.rectangle([115, 240, 185, 275], fill=(15, 23, 42), outline=pal["ring"], width=2)
    draw.text((138, 248), initials, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def crop_face_region(img: Image.Image) -> Image.Image:
    """Crops the central 70% where the face is concentrated to minimize background color bias."""
    w, h = img.size
    left = int(w * 0.12)
    top = int(h * 0.08)
    right = int(w * 0.88)
    bottom = int(h * 0.88)
    return img.crop((left, top, right, bottom))


def compute_normalized_histogram(img: Image.Image, bins: int = 16) -> np.ndarray:
    """Computes normalized 3-channel color histogram focused on face region."""
    face = crop_face_region(img)
    resized = face.resize((128, 128))
    arr = np.asarray(resized, dtype=np.float32)
    
    hist_r, _ = np.histogram(arr[:, :, 0], bins=bins, range=(0, 256))
    hist_g, _ = np.histogram(arr[:, :, 1], bins=bins, range=(0, 256))
    hist_b, _ = np.histogram(arr[:, :, 2], bins=bins, range=(0, 256))
    
    hist = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float32)
    norm = np.linalg.norm(hist)
    if norm > 0:
        hist /= norm
    return hist


def compute_structural_vector(img: Image.Image, size: Tuple[int, int] = (32, 32)) -> np.ndarray:
    """Converts image to normalized, contrast-equalized facial luminance vector."""
    face = crop_face_region(img)
    gray = ImageOps.grayscale(face)
    equalized = ImageOps.equalize(gray)
    resized = equalized.resize(size, Image.Resampling.LANCZOS)
    arr = np.asarray(resized, dtype=np.float32)
    arr = arr - np.mean(arr)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr /= norm
    return arr.flatten()


def compute_edge_energy_vector(img: Image.Image, size: Tuple[int, int] = (32, 32)) -> np.ndarray:
    """Extracts facial edge contour energy via Laplacian filter."""
    face = crop_face_region(img)
    gray = ImageOps.grayscale(face)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    resized = edges.resize(size, Image.Resampling.LANCZOS)
    arr = np.asarray(resized, dtype=np.float32)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr /= norm
    return arr.flatten()


def compare_biometrics(
    reference_bytes: bytes,
    captured_bytes: bytes,
    threshold: float = 58.0
) -> Dict[str, Any]:
    """
    Compares an enrolled reference photo against a live captured frame.
    Calibrated with facial region focus and histogram equalization.

    Returns:
      Dict with:
        - confidence_pct: float (0.0 to 99.9%)
        - is_match: bool
        - threshold: float
        - metrics: sub-score breakdown
    """
    ref_img = load_image_bytes(reference_bytes)
    cap_img = load_image_bytes(captured_bytes)

    if ref_img is None or cap_img is None:
        return {
            "confidence_pct": 0.0,
            "is_match": False,
            "threshold": threshold,
            "error": "Could not decode one or both biometric images."
        }

    # 1. Structural similarity
    ref_struct = compute_structural_vector(ref_img)
    cap_struct = compute_structural_vector(cap_img)
    struct_sim = float(np.dot(ref_struct, cap_struct))
    struct_score = max(0.0, min(1.0, (struct_sim + 1.0) / 2.0))

    # 2. Color distribution correlation (face region)
    ref_hist = compute_normalized_histogram(ref_img)
    cap_hist = compute_normalized_histogram(cap_img)
    color_sim = float(np.dot(ref_hist, cap_hist))
    color_score = max(0.0, min(1.0, color_sim))

    # 3. Edge/contour energy correlation
    ref_edge = compute_edge_energy_vector(ref_img)
    cap_edge = compute_edge_energy_vector(cap_img)
    edge_sim = float(np.dot(ref_edge, cap_edge))
    edge_score = max(0.0, min(1.0, (edge_sim + 1.0) / 2.0))

    # Weighted aggregate score
    composite = (0.50 * struct_score) + (0.30 * color_score) + (0.20 * edge_score)

    confidence = round(composite * 100.0, 2)
    confidence = max(10.0, min(99.6, confidence))

    is_match = confidence >= threshold

    return {
        "confidence_pct": confidence,
        "is_match": is_match,
        "threshold": threshold,
        "metrics": {
            "structural_similarity": round(struct_score * 100, 1),
            "color_correlation": round(color_score * 100, 1),
            "edge_contour_match": round(edge_score * 100, 1)
        }
    }
