# Extract features from images and save into "features_all.csv"
# with alignment, quality filtering, and skip unchanged folders

import os
import dlib
import csv
import numpy as np
import logging
import cv2
import json
from datetime import datetime
import hashlib

from config import DLIB_LANDMARK_PATH, DLIB_RECOG_MODEL_PATH, CSV_PATH, ALIGNED_SIZE, MIN_LAPLACIAN_VAR, MIN_BRIGHTNESS, MAX_BRIGHTNESS
from face_utils import detect_faces, compute_embedding

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_images_from_camera = "data/data_faces_from_camera/"
metadata_file = "data/processing_metadata.json"

predictor = dlib.shape_predictor(DLIB_LANDMARK_PATH)
face_reco_model = dlib.face_recognition_model_v1(DLIB_RECOG_MODEL_PATH)

def get_folder_hash(folder_path):
    """Return MD5 hash of file names + modification times in a folder."""
    if not os.path.exists(folder_path):
        return None
    file_info = []
    for file_name in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            mod_time = os.path.getmtime(file_path)
            file_info.append(f"{file_name}:{mod_time}")
    if not file_info:
        return None
    return hashlib.md5("|".join(file_info).encode()).hexdigest()

def load_processing_metadata():
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_processing_metadata(metadata):
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def extract_roll_name_from_folder(folder_name):
    roll_no = "UNKNOWN"; person_name = "UNKNOWN"
    parts = folder_name.split('_', 1)
    if len(parts) == 2:
        if parts[0].isdigit(): roll_no = parts[0]
        person_name = parts[1].replace('_', ' ')
    else:
        if parts[0].isdigit():
            roll_no = parts[0]
            person_name = "UNKNOWN_NAME"
        else:
            person_name = parts[0].replace('_', ' ')
            roll_no = "UNKNOWN_ROLL"
    return roll_no, person_name

def features_from_image(path_img):
    img_bgr = cv2.imread(path_img)
    if img_bgr is None:
        return None
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    rects = detect_faces(img_rgb)
    if not rects:
        return None
    rect = max(rects, key=lambda r: (r.right()-r.left())*(r.bottom()-r.top()))
    emb, shape, aligned = compute_embedding(img_rgb, rect)
    gray = cv2.cvtColor(cv2.cvtColor(aligned, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    mean = gray.mean()
    if blur < MIN_LAPLACIAN_VAR or mean < MIN_BRIGHTNESS or mean > MAX_BRIGHTNESS:
        return None
    return emb

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs(path_images_from_camera, exist_ok=True)

    metadata = load_processing_metadata()
    rows = []
    updated_metadata = {}

    person_folders = [f for f in os.listdir(path_images_from_camera) if os.path.isdir(os.path.join(path_images_from_camera, f))]
    person_folders.sort()

    for folder_name in person_folders:
        folder_path = os.path.join(path_images_from_camera, folder_name)
        h = get_folder_hash(folder_path)

        # FULL SKIP if hash matches metadata
        if folder_name in metadata and metadata[folder_name].get('hash') == h:
            logging.info("Skipping %s (unchanged, using previous record)", folder_name)
            # reuse old embedding data
            roll = metadata[folder_name]['roll_no']
            name = metadata[folder_name]['name']
            embedding = metadata[folder_name]['embedding']
            rows.append([roll, name] + embedding)
            updated_metadata[folder_name] = metadata[folder_name]
            continue

        roll, name = extract_roll_name_from_folder(folder_name)
        embs = []
        for fn in os.listdir(folder_path):
            if fn.lower().endswith(('.png', '.jpg', '.jpeg')):
                emb = features_from_image(os.path.join(folder_path, fn))
                if emb is not None:
                    embs.append(emb)

        if embs:
            mean_emb = np.mean(embs, axis=0).tolist()
            rows.append([roll, name] + mean_emb)
            updated_metadata[folder_name] = {
                'hash': h,
                'processed_time': datetime.now().isoformat(),
                'roll_no': roll,
                'name': name,
                'images_used': len(embs),
                'embedding': mean_emb
            }
            logging.info("%s -> %d images processed", folder_name, len(embs))
        else:
            logging.warning("%s -> no valid images", folder_name)

    # Save CSV
    header = ["Roll_No", "Name"] + [f"feature_{i}" for i in range(128)]
    with open(CSV_PATH, 'w', newline='') as f:
        cw = csv.writer(f)
        cw.writerow(header)
        for r in rows:
            cw.writerow(r)

    save_processing_metadata(updated_metadata)
    logging.info("Saved %d identities to %s", len(rows), CSV_PATH)

if __name__ == '__main__':
    main()
