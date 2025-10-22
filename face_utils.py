"""
face_utils.py
Face detection, alignment, embedding, and quality checks.
"""

import os
import numpy as np
import cv2
import dlib
import time
from typing import Tuple, Optional

from config import (
    DLIB_LANDMARK_PATH, DLIB_RECOG_MODEL_PATH, DLIB_CNN_DETECTOR_PATH,
    UPSAMPLE_DET, USE_CNN_DETECTOR_IF_AVAILABLE, ALIGN_FACE, ALIGNED_SIZE,
    CHECK_QUALITY, MIN_LAPLACIAN_VAR, MIN_BRIGHTNESS, MAX_BRIGHTNESS,
    DISTANCE_METRIC, THRESHOLD_EUCLIDEAN, THRESHOLD_COSINE, SHOW_DEBUG
)

# --- Lazy-loaded models ---
predictor = None
face_reco_model = None
detector = None


def _load_models():
    """Load dlib models lazily."""
    global predictor, face_reco_model, detector
    if predictor is None:
        if not os.path.exists(DLIB_LANDMARK_PATH):
            raise FileNotFoundError(f"Shape predictor model not found: {DLIB_LANDMARK_PATH}")
        predictor = dlib.shape_predictor(DLIB_LANDMARK_PATH)

    if face_reco_model is None:
        if not os.path.exists(DLIB_RECOG_MODEL_PATH):
            raise FileNotFoundError(f"Face recognition model not found: {DLIB_RECOG_MODEL_PATH}")
        face_reco_model = dlib.face_recognition_model_v1(DLIB_RECOG_MODEL_PATH)

    if detector is None:
        if USE_CNN_DETECTOR_IF_AVAILABLE and DLIB_CNN_DETECTOR_PATH and os.path.exists(DLIB_CNN_DETECTOR_PATH):
            try:
                detector = dlib.cnn_face_detection_model_v1(DLIB_CNN_DETECTOR_PATH)
            except Exception as e:
                print(f"[WARN] CNN face detector load failed: {e}, falling back to HOG detector.")
                detector = dlib.get_frontal_face_detector()
        else:
            detector = dlib.get_frontal_face_detector()


def _rect_from_dlib(rect):
    """Extract pure dlib.rectangle from cnn/hog detector outputs."""
    return rect.rect if hasattr(rect, 'rect') else rect


def detect_faces(img_rgb):
    """Detect faces and return list of dlib.rectangle."""
    _load_models()

    # CRITICAL FIX: Ensure image is in the exact format dlib expects
    # This handles cases where the array might not be C-contiguous
    if not isinstance(img_rgb, np.ndarray):
        raise ValueError("Input must be a numpy array")

    # Ensure correct dtype
    if img_rgb.dtype != np.uint8:
        img_rgb = img_rgb.astype(np.uint8)

    # Ensure C-contiguous memory layout
    if not img_rgb.flags['C_CONTIGUOUS']:
        img_rgb = np.ascontiguousarray(img_rgb)

    # Validate shape (must be HxWx3 for RGB or HxW for grayscale)
    if len(img_rgb.shape) == 3:
        if img_rgb.shape[2] != 3:
            raise ValueError(f"RGB image must have 3 channels, got {img_rgb.shape[2]}")
    elif len(img_rgb.shape) != 2:
        raise ValueError(f"Image must be 2D (grayscale) or 3D (RGB), got shape {img_rgb.shape}")

    results = detector(img_rgb, UPSAMPLE_DET)
    return [_rect_from_dlib(r) for r in results]


def shape_for_rect(img_rgb, rect):
    """Get facial landmarks for a given rect."""
    _load_models()
    return predictor(img_rgb, rect)


def _eye_centers(shape):
    """Return (x,y) for left and right eye centers."""
    left_pts = [(shape.part(i).x, shape.part(i).y) for i in range(36, 42)]
    right_pts = [(shape.part(i).x, shape.part(i).y) for i in range(42, 48)]
    lx, ly = np.mean([p[0] for p in left_pts]), np.mean([p[1] for p in left_pts])
    rx, ry = np.mean([p[0] for p in right_pts]), np.mean([p[1] for p in right_pts])
    return (lx, ly), (rx, ry)


def align_face(img_rgb, shape, output_size=ALIGNED_SIZE):
    """Align face based on eye centers, crop to square."""
    if not ALIGN_FACE:
        return img_rgb

    (lx, ly), (rx, ry) = _eye_centers(shape)
    dy, dx = ry - ly, rx - lx
    angle = np.degrees(np.arctan2(dy, dx))
    eyes_center = ((lx + rx) / 2.0, (ly + ry) / 2.0)

    M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
    aligned = cv2.warpAffine(img_rgb, M, (img_rgb.shape[1], img_rgb.shape[0]), flags=cv2.INTER_LINEAR)

    half = output_size // 2
    cx, cy = int(eyes_center[0]), int(eyes_center[1])
    x1, y1 = max(0, cx - half), max(0, cy - half)
    x2, y2 = min(aligned.shape[1], cx + half), min(aligned.shape[0], cy + half)

    if y2 <= y1 or x2 <= x1:
        return img_rgb  # invalid crop region

    crop = aligned[y1:y2, x1:x2]
    if crop.size == 0:
        return img_rgb
    return cv2.resize(crop, (output_size, output_size))


def compute_embedding(img_rgb, rect):
    """Compute 128D face embedding for a given rect."""
    _load_models()
    shape = predictor(img_rgb, rect)
    aligned = align_face(img_rgb, shape, output_size=ALIGNED_SIZE)
    h, w = aligned.shape[:2]
    aligned_rect = dlib.rectangle(0, 0, w, h)
    emb = face_reco_model.compute_face_descriptor(aligned, predictor(aligned, aligned_rect))
    return np.array(emb, dtype=np.float32), shape, aligned


def image_quality_ok(img_rgb, rect):
    """Check blur and brightness thresholds for a detected face."""
    if not CHECK_QUALITY:
        return True
    x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(img_rgb.shape[1] - 1, x2), min(img_rgb.shape[0] - 1, y2)
    if y2 <= y1 or x2 <= x1:
        return False

    roi = img_rgb[y1:y2, x1:x2]
    if roi.size == 0:
        return False
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    mean = gray.mean()
    if SHOW_DEBUG:
        print(f"[quality] blur={blur:.1f}, mean={mean:.1f}")
    return (blur >= MIN_LAPLACIAN_VAR) and (MIN_BRIGHTNESS <= mean <= MAX_BRIGHTNESS)


def cosine_distance(a, b):
    """Return cosine distance (1 - cosine similarity)."""
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    na, nb = np.linalg.norm(a) + 1e-8, np.linalg.norm(b) + 1e-8
    return 1.0 - float(np.dot(a, b) / (na * nb))


def euclidean_distance(a, b):
    """Return Euclidean (L2) distance."""
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    return float(np.linalg.norm(a - b))


def compare_distance(a, b):
    """Compare embeddings with configured metric and return (distance, threshold)."""
    if DISTANCE_METRIC == 'cosine':
        return cosine_distance(a, b), THRESHOLD_COSINE
    return euclidean_distance(a, b), THRESHOLD_EUCLIDEAN