"""
Centralized configuration for Face Recognition Attendance Management System
Now loads sensitive values from .env using python-dotenv for security.
"""

import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# --- MySQL Database Config ---
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASS"),
    "database": os.getenv("MYSQL_DB"),
    "ssl_ca": os.getenv("MYSQL_SSL_CA"),  # Optional
}

# Fail fast if any critical DB config is missing
required_keys = ["host", "user", "password", "database"]
for key in required_keys:
    if not MYSQL_CONFIG[key]:
        raise RuntimeError(f"❌ Missing MySQL config key: {key}. Check your .env file.")

# --- Models ---
DLIB_LANDMARK_PATH = 'data/data_dlib/shape_predictor_68_face_landmarks.dat'
DLIB_RECOG_MODEL_PATH = 'data/data_dlib/dlib_face_recognition_resnet_model_v1.dat'
DLIB_CNN_DETECTOR_PATH = 'data/data_dlib/mmod_human_face_detector.dat'  # optional; used if present

# --- Detection ---
UPSAMPLE_DET = 0            # upsample count for detector (0 or 1 recommended)
USE_CNN_DETECTOR_IF_AVAILABLE = True

# --- Alignment ---
ALIGN_FACE = True           # align faces using eye landmarks
ALIGNED_SIZE = 150          # square output size for alignment

# --- Quality filters (per-face ROI) ---
CHECK_QUALITY = True
MIN_LAPLACIAN_VAR = 80.0    # blur threshold: higher is sharper
MIN_BRIGHTNESS = 40         # min mean pixel
MAX_BRIGHTNESS = 210        # max mean pixel

# --- Embedding/Matching ---
DISTANCE_METRIC = 'cosine'  # 'euclidean' or 'cosine'
THRESHOLD_EUCLIDEAN = 0.60
THRESHOLD_COSINE = 0.35

# Require N consecutive positive matches before considering "recognized"
MIN_CONSEC_MATCHES = 2

# --- Liveness (blink check) ---
USE_LIVENESS = True
EAR_BLINK_THRESHOLD = 0.20
EAR_CONSEC_FRAMES = 3
REQUIRE_BLINK_BEFORE_MARK = True
BLINK_VALID_WINDOW_SEC = 10

# --- Attendance logic ---
RECLASSIFY_INTERVAL = 10    # frames; how often to recompute embeddings
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
FRAME_SIZE = (640, 480)
CSV_PATH = os.getenv("CSV_PATH", "data/features_all.csv")

# --- Logging/UI ---
SHOW_DEBUG = os.getenv("SHOW_DEBUG", "False").lower() == "true"
