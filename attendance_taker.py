"""
attendance_taker.py
MySQL + class-enabled face recognition attendance script.
"""

import numpy as np
import cv2
import os
import pandas as pd
import time
import logging
import datetime
from collections import deque, defaultdict
from db_config import get_connection

from config import (
    CSV_PATH, FRAME_SIZE, CAMERA_INDEX,
    MIN_CONSEC_MATCHES, REQUIRE_BLINK_BEFORE_MARK, BLINK_VALID_WINDOW_SEC
)
from face_utils import detect_faces, compute_embedding, image_quality_ok, compare_distance
from liveness import ear_from_shape  # safer EAR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        """Insert attendance row into MySQL and record visual notification."""
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance (roll_no, name, class_id, time, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (roll_no, name, self.class_id, current_time, current_date))
            conn.commit()
            logging.info("✅ Attendance recorded for %s (%s) in class_id=%s", name, roll_no, self.class_id)
            self.marked_today.add((roll_no, self.class_id))
            self.last_mark_message = f"ATTENDANCE MARKED: {name} ({roll_no})"
            self.last_mark_time = time.time()
        except Exception as e:
            logging.info("⚠️ Attendance insert error (likely already marked): %s", e)
            self.last_mark_message = f"ALREADY MARKED / ERROR: {name} ({roll_no})"
            self.last_mark_time = time.time()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def process(self, cap):
        if not self.get_face_database():
            logging.error("Face DB not available or malformed. Run features_extraction_to_csv.py first.")
            return

        try:
            while cap.isOpened():
                self.frame_cnt += 1
                ret, frame_bgr = cap.read()
                if not ret:
                    logging.warning("No camera frame returned; stopping.")
                    break

                frame_bgr = cv2.resize(frame_bgr, FRAME_SIZE)
                img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                faces = detect_faces(img_rgb)
                names_to_draw = []
                ear_val = None

                for rect in faces:
                    try:
                        if not image_quality_ok(img_rgb, rect):
                            cv2.rectangle(frame_bgr, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 0, 255), 2)
                            cv2.putText(frame_bgr, "LOW QUALITY", (rect.left(), max(20, rect.top() - 10)), self.font, 0.6, (0, 0, 255), 1)
                            continue

                        emb, shape, aligned = compute_embedding(img_rgb, rect)
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
                                self.mark_attendance(best_roll, best_name)
                                self.match_streaks[best_roll] = 0
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
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            logging.error("Failed to open camera index %s", CAMERA_INDEX)
            return
        self.process(cap)


def choose_class() -> int:
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
        try:
            conn.close()
        except Exception:
            pass


def main():
    class_id = choose_class()
    FaceRecognizer(class_id).run()


if __name__ == '__main__':
    main()
