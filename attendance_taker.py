"""
attendance_taker.py
Class-enabled face recognition attendance script. Now publishes attendance
to the Producer Service API, routing all marks through the Valkey queue.
"""

import numpy as np
import cv2
import os
import pandas as pd
import time
import logging
import datetime
from collections import deque, defaultdict
import requests # New import for API calls

from config import (
    CSV_PATH, FRAME_SIZE, CAMERA_INDEX,
    MIN_CONSEC_MATCHES, REQUIRE_BLINK_BEFORE_MARK, BLINK_VALID_WINDOW_SEC
)
from face_utils import detect_faces, compute_embedding, image_quality_ok, compare_distance
from liveness import ear_from_shape  # safer EAR
from db_config import get_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration for Producer Service API ---
# FIX: Changed invalid 127.0.0.0 to correct 127.0.0.1
PRODUCER_API_URL = "http://127.0.0.1:5001/api/v1/log_attendance"
# NOTE: Update 127.0.0.1 to your server's IP if running on separate machines


class FaceRecognizer:
    def __init__(self, class_id: int):
        self.class_id = int(class_id)
        self.font = cv2.FONT_ITALIC
        self.frame_cnt = 0

        # Known face data
        self.face_features_known_list = []
        self.face_roll_no_known_list = []
        self.face_name_known_list = []

        # Matching & blink tracking
        self.match_streaks = defaultdict(int)
        self.last_blink_time = 0
        self.ear_queue = deque(maxlen=12)
        self.blinks_total = 0
        self._below_count = 0

        # Prevent duplicate marks in a session
        self.marked_today = set()

        # FPS calculation
        self.last_time = time.time()
        self.fps = 0.0

        # Last mark message for display
        self.last_mark_message = ""
        self.last_mark_time = 0

    def get_face_database(self) -> bool:
        """Load features from CSV_PATH into memory."""
        if not os.path.exists(CSV_PATH):
            logging.warning("CSV_PATH does not exist: %s", CSV_PATH)
            return False
        try:
            df = pd.read_csv(CSV_PATH)
            if not {'Roll_No', 'Name'}.issubset(df.columns):
                logging.warning("CSV missing Roll_No/Name columns: %s", CSV_PATH)
                return False

            self.face_roll_no_known_list = df['Roll_No'].astype(str).tolist()
            self.face_name_known_list = df['Name'].astype(str).tolist()
            feats = df.drop(columns=['Roll_No', 'Name'])

            if feats.empty:
                logging.warning("Features CSV found but no embeddings present.")
                self.face_features_known_list = []
                return True

            self.face_features_known_list = feats.values.astype(np.float32)
            logging.info("Loaded %d embeddings from %s", len(self.face_features_known_list), CSV_PATH)
            return True
        except Exception as e:
            logging.exception("Error reading CSV_PATH: %s", e)
            return False

    def update_fps(self):
        now = time.time()
        dt = now - self.last_time
        if dt > 0:
            self.fps = 1.0 / dt
        self.last_time = now

    def draw_hud(self, img):
        cv2.putText(img, f"Frames: {self.frame_cnt}", (20, 40), self.font, 0.7, (255, 255, 255), 1)
        cv2.putText(img, f"FPS: {self.fps:.1f}", (20, 65), self.font, 0.7, (0, 255, 0), 1)
        cv2.putText(img, f"Blinks: {self.blinks_total}", (20, 90), self.font, 0.7, (0, 255, 255), 1)
        cv2.putText(img, f"Class ID: {self.class_id}", (20, 115), self.font, 0.7, (255, 200, 0), 1)
        cv2.putText(img, "Q: Quit", (20, 450), self.font, 0.8, (200, 200, 200), 1)

        # Display last mark message
        if self.last_mark_message and (time.time() - self.last_mark_time < 3):
            cv2.putText(img, self.last_mark_message, (20, 140), self.font, 0.7, (0, 255, 0), 2)

    def mark_attendance(self, roll_no: str, name: str):
        """Sends attendance data to the Producer Service API for queueing."""
        # Use roll_no and class_id only, as name is looked up by the consumer
        try:
            payload = {
                "roll_no": roll_no,
                "class_id": self.class_id,
            }

            response = requests.post(PRODUCER_API_URL, json=payload, timeout=2) # Added timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            if response.status_code == 202:
                logging.info("✅ Attendance sent to queue for %s (%s)", name, roll_no)
                self.marked_today.add((roll_no, self.class_id))
                self.last_mark_message = f"QUEUED: {name} ({roll_no})"
            else:
                logging.warning("⚠️ Queue API responded unexpectedly: %s", response.text)
                self.last_mark_message = f"QUEUE ERROR: {response.status_code}"

            self.last_mark_time = time.time()

        except requests.exceptions.RequestException as e:
            # This handles connection errors, timeouts, etc.
            logging.error("❌ Failed to connect to Producer API: %s", e)
            self.last_mark_message = "API OFFLINE"
            self.last_mark_time = time.time()


    def process(self, cap):
        if not self.get_face_database():
            logging.error("Face DB not available or malformed. Run features_extraction_to_csv.py first.")
            return

        try:
            while cap.isOpened():
                self.frame_cnt += 1
                ret, frame_bgr = cap.read()

                # --- FIX: Robust Frame Checks ---
                if not ret:
                    logging.warning("No camera frame returned (ret=False); stopping.")
                    break

                if frame_bgr is None or frame_bgr.size == 0 or frame_bgr.dtype != np.uint8:
                    logging.warning("Captured frame is empty, corrupted, or not 8-bit unsigned integer type; skipping frame.")
                    time.sleep(0.1)
                    continue

                if len(frame_bgr.shape) < 3:
                    logging.warning("Frame does not have enough channels for BGR; skipping.")
                    time.sleep(0.1)
                    continue
                # ----------------------------------------------

                frame_bgr = cv2.resize(frame_bgr, FRAME_SIZE)
                img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # FIX: Use np.ascontiguousarray to ensure dlib compatibility
                img_rgb_contiguous = np.ascontiguousarray(img_rgb)

                faces = detect_faces(img_rgb_contiguous)
                names_to_draw = []
                ear_val = None

                for rect in faces:
                    try:
                        if not image_quality_ok(img_rgb_contiguous, rect):
                            cv2.rectangle(frame_bgr, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 0, 255), 2)
                            cv2.putText(frame_bgr, "LOW QUALITY", (rect.left(), max(20, rect.top() - 10)), self.font, 0.6, (0, 0, 255), 1)
                            continue

                        emb, shape, aligned = compute_embedding(img_rgb_contiguous, rect)
                        ear_val = ear_from_shape(shape)

                        # Default match
                        best_name, best_roll, best_d, best_thr = "Unknown", None, float('inf'), None

                        if len(self.face_features_known_list) > 0:
                            for idx, known in enumerate(self.face_features_known_list):
                                d, thr = compare_distance(emb, known)
                                if d < best_d:
                                    best_d = d
                                    best_roll = self.face_roll_no_known_list[idx]
                                    best_name = self.face_name_known_list[idx]
                                    best_thr = thr

                        cv2.rectangle(frame_bgr, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (255, 255, 255), 2)
                        is_match = (best_thr is not None) and (best_d < best_thr)
                        display = f"Unknown ({best_d:.3f})"

                        if is_match and best_roll:
                            self.match_streaks[best_roll] += 1
                            display = f"{best_name} [{best_roll}] ({best_d:.3f})"
                            can_mark = self.match_streaks[best_roll] >= MIN_CONSEC_MATCHES
                            if REQUIRE_BLINK_BEFORE_MARK:
                                can_mark = can_mark and (time.time() - self.last_blink_time) <= BLINK_VALID_WINDOW_SEC
                            if can_mark and ((best_roll, self.class_id) not in self.marked_today):
                                # --- Action: Mark Attendance via API ---
                                self.mark_attendance(best_roll, best_name)
                                self.match_streaks[best_roll] = 0
                                # ---------------------------------------
                        else:
                            if best_roll:
                                self.match_streaks[best_roll] = 0

                        names_to_draw.append((display, (rect.left(), rect.bottom() + 20)))
                    except Exception as face_e:
                        logging.exception("Error processing face: %s", face_e)

                # Blink tracking
                if ear_val is not None:
                    self.ear_queue.append(ear_val)
                    from config import EAR_BLINK_THRESHOLD, EAR_CONSEC_FRAMES
                    if ear_val < EAR_BLINK_THRESHOLD:
                        self._below_count += 1
                    else:
                        if self._below_count >= EAR_CONSEC_FRAMES:
                            self.blinks_total += 1
                            self.last_blink_time = time.time()
                        self._below_count = 0

                # Draw labels
                for name, pos in names_to_draw:
                    cv2.putText(frame_bgr, name, pos, self.font, 0.7, (0, 255, 255), 1)

                self.draw_hud(frame_bgr)
                cv2.imshow("camera", frame_bgr)
                self.update_fps()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("Quit key pressed.")
                    break

        except KeyboardInterrupt:
            logging.info("Stopped by user.")
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def run(self):
        # --- FIX: Robust Camera Initialization (Iterate over backends/indices) ---
        INDEXES_TO_TRY = [CAMERA_INDEX, 0, 1]
        BACKENDS_TO_TRY = [cv2.CAP_DSHOW, cv2.CAP_V4L2, cv2.CAP_ANY]

        cap = None
        for index in INDEXES_TO_TRY:
            for backend in BACKENDS_TO_TRY:
                try:
                    cap = cv2.VideoCapture(index, backend)
                    if cap.isOpened():
                        # Read one frame to verify it's working
                        ret, _ = cap.read()
                        if ret:
                            logging.info("Successfully opened camera %d using backend %s", index, backend)
                            self.process(cap)
                            return
                        else:
                            cap.release()
                            cap = None
                    else:
                        cap.release()
                        cap = None
                except Exception:
                    # Ignore errors for unsupported backends
                    cap = None
                    pass

        logging.error("Failed to open camera after trying multiple indices and backends.")
        return


def choose_class() -> int:
    from db_config import get_connection

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT class_id, class_name FROM classes ORDER BY class_id")
        classes = cursor.fetchall()
        if not classes:
            raise RuntimeError("No classes found. Run init_db first.")

        print("\nAvailable Classes:")
        for cid, cname in classes:
            print(f"{cid}: {cname}")

        while True:
            choice = input("Enter class ID to take attendance for (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                raise SystemExit(0)
            try:
                cid = int(choice)
                if any(cid == row[0] for row in classes):
                    return cid
                print("Invalid class id, try again.")
            except ValueError:
                print("Please enter a numeric class id.")
    finally:
        if conn:
            conn.close()


def main():
    class_id = choose_class()
    FaceRecognizer(class_id).run()


if __name__ == '__main__':
    # Ensure 'requests' is installed for the API call
    try:
        import requests
    except ImportError:
        print("\nFATAL ERROR: The 'requests' library is required for API communication.")
        print("Please run: pip install requests")
        exit(1)

    main()
