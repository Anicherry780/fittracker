"""
Joint angle calculation — consolidated single implementation.
Uses dot product method (from CVIP project, now unified).
"""

import numpy as np
from typing import Tuple


def calculate_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """
    Calculate the angle at point B formed by points A-B-C.
    Uses dot product: θ = arccos((BA · BC) / (|BA| × |BC|)) × 180/π

    Args:
        a: First point (x, y)
        b: Vertex point (x, y)
        c: Third point (x, y)

    Returns:
        Angle in degrees (0-180)
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    # Dot product and magnitudes
    dot_product = np.dot(ba, bc)
    magnitude_ba = np.linalg.norm(ba)
    magnitude_bc = np.linalg.norm(bc)

    # Avoid division by zero
    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    # Clamp to [-1, 1] to avoid arccos domain errors
    cos_angle = np.clip(dot_product / (magnitude_ba * magnitude_bc), -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_angle))

    return round(float(angle), 2)


# MediaPipe landmark indices for common joint angles
JOINT_ANGLES = {
    "left_elbow": (11, 13, 15),   # shoulder, elbow, wrist
    "right_elbow": (12, 14, 16),
    "left_shoulder": (13, 11, 23),  # elbow, shoulder, hip
    "right_shoulder": (14, 12, 24),
    "left_hip": (11, 23, 25),      # shoulder, hip, knee
    "right_hip": (12, 24, 26),
    "left_knee": (23, 25, 27),     # hip, knee, ankle
    "right_knee": (24, 26, 28),
}


def extract_joint_angles(landmarks: list) -> dict:
    """
    Extract all joint angles from MediaPipe pose landmarks.
    Each landmark should have .x and .y attributes.

    Returns dict of angle_name → angle_degrees
    """
    angles = {}
    for name, (a_idx, b_idx, c_idx) in JOINT_ANGLES.items():
        try:
            a = (landmarks[a_idx].x, landmarks[a_idx].y)
            b = (landmarks[b_idx].x, landmarks[b_idx].y)
            c = (landmarks[c_idx].x, landmarks[c_idx].y)
            angles[name] = calculate_angle(a, b, c)
        except (IndexError, AttributeError):
            angles[name] = None
    return angles
