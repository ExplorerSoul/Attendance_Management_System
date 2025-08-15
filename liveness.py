"""
liveness.py
Eye Aspect Ratio (EAR) calculation for blink detection.
"""

import numpy as np
from config import EAR_BLINK_THRESHOLD, EAR_CONSEC_FRAMES


def _ear(eye_pts: np.ndarray) -> float:
    """
    Compute Eye Aspect Ratio (EAR) for a given 6-point eye landmark set.
    Args:
        eye_pts: np.ndarray of shape (6, 2) containing (x, y) coordinates.
    Returns:
        EAR value (float) or 0.0 if invalid.
    """
    if eye_pts.shape != (6, 2):
        return 0.0  # Invalid shape

    # Vertical distances
    A = np.linalg.norm(eye_pts[1] - eye_pts[5])
    B = np.linalg.norm(eye_pts[2] - eye_pts[4])
    # Horizontal distance
    C = np.linalg.norm(eye_pts[0] - eye_pts[3])

    if C < 1e-6:
        return 0.0  # Avoid division by zero

    return (A + B) / (2.0 * C)


def ear_from_shape(shape) -> float:
    """
    Extracts left and right eye landmarks from a dlib shape and computes average EAR.
    Args:
        shape: dlib.full_object_detection (68 facial landmarks expected).
    Returns:
        Average EAR (float).
    """
    try:
        left = np.array([[shape.part(i).x, shape.part(i).y] for i in range(36, 42)], dtype=np.float32)
        right = np.array([[shape.part(i).x, shape.part(i).y] for i in range(42, 48)], dtype=np.float32)
    except Exception:
        return 0.0  # If shape doesn't have expected points

    ear_left = _ear(left)
    ear_right = _ear(right)
    return (ear_left + ear_right) / 2.0
