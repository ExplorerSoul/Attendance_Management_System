"""
Patched face_register.py
Fixes and improvements:
 - Initialize frame variables properly
 - Simpler and safer ROI extraction (handles boundaries using numpy slicing and pad)
 - Remove incorrect color conversions
 - Small GUI robustness fixes
 - Avoid heavy per-pixel loops when building ROI
"""

# Note: this module is a single-file replacement for your face_register.py

import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import tkinter as tk
from tkinter import font as tkFont, messagebox
from PIL import Image, ImageTk
import subprocess
import mysql.connector
from config import MYSQL_CONFIG


# For sound (works on Windows, fallback for other systems)
try:
    import winsound

    SOUND_AVAILABLE = True
except Exception:
    try:
        import platform
        SOUND_AVAILABLE = True
    except Exception:
        SOUND_AVAILABLE = False

# Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()


class Face_Register:
    def __init__(self):
        self.current_frame_faces_cnt = 0
        self.existing_faces_cnt = 0
        self.ss_cnt = 0

        # Tkinter GUI
        self.win = tk.Tk()
        self.win.title("Face Register")
        self.win.geometry("1200x650")

        # GUI left part (camera feed)
        self.frame_left_camera = tk.Frame(self.win)
        self.label = tk.Label(self.win)
        self.label.pack(side=tk.LEFT, padx=10, pady=10)
        self.frame_left_camera.pack()

        # GUI right part (info and controls)
        self.frame_right_info = tk.Frame(self.win)
        self.label_cnt_face_in_database = tk.Label(self.frame_right_info, text=str(self.existing_faces_cnt))
        self.label_fps_info = tk.Label(self.frame_right_info, text="")
        self.input_rollno = tk.Entry(self.frame_right_info)
        self.input_name = tk.Entry(self.frame_right_info)
        self.input_rollno_char = ""
        self.input_name_char = ""
        self.label_warning = tk.Label(self.frame_right_info)
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in current frame: ")
        self.log_all = tk.Label(self.frame_right_info, wraplength=400)
        self.capture_prompt_label = tk.Label(self.frame_right_info, text="", font=('Helvetica', 16, 'bold'), fg='blue')

        self.font_title = tkFont.Font(family='Helvetica', size=20, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=15, weight='bold')
        self.font_warning = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.path_photos_from_camera = "data/data_faces_from_camera/"
        self.current_face_dir = ""
        self.font = cv2.FONT_ITALIC

        # Proper initial values
        self.current_frame = None
        self.face_ROI_image = None
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False
        self.face_folder_created_flag = False
        self.capturing_images = False
        self.capture_paused = False
        self.capture_category_index = 0
        self.images_captured_in_category = 0
        self.capture_categories = {
            0: "Turn Left",
            1: "Turn Right",
            2: "Smile",
            3: "Raise Eyebrows",
            4: "Normal"
        }
        self.num_images_per_category = 10
        self.capture_delay_ms = 500

        self.resume_capture_button = None

        # FPS
        self.frame_time = 0
        self.frame_start_time = time.time()
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open camera. Please ensure it's connected and not in use.")
            self.win.destroy()
            return

    def play_beep_sound(self):
        if not SOUND_AVAILABLE:
            return
        try:
            if 'winsound' in globals():
                winsound.Beep(1000, 300)
            else:
                system = platform.system()
                if system == "Darwin":
                    subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"], check=False)
                elif system == "Linux":
                    subprocess.run(["paplay", "/usr/share/sounds/alsa/Front_Left.wav"], check=False)
        except Exception as e:
            logging.warning(f"Could not play sound: {e}")

    def GUI_clear_data(self):
        if os.path.isdir(self.path_photos_from_camera):
            for entry in os.listdir(self.path_photos_from_camera):
                path = os.path.join(self.path_photos_from_camera, entry)
                if os.path.isdir(path):
                    shutil.rmtree(path)
        features_csv = os.path.join('data', 'features_all.csv')
        if os.path.isfile(features_csv):
            os.remove(features_csv)
        self.label_cnt_face_in_database['text'] = "0"
        self.existing_faces_cnt = 0
        self.log_all["text"] = "Face images and features_all.csv removed!"
        self.face_folder_created_flag = False

    def GUI_get_input_data(self):
        self.input_rollno_char = self.input_rollno.get().strip()
        self.input_name_char = self.input_name.get().strip()

        if not self.input_rollno_char or not self.input_name_char:
            messagebox.showwarning("Input Error", "Please enter both Roll Number and Name.")
            return

        self.create_face_folder()
        self.label_cnt_face_in_database['text'] = str(self.existing_faces_cnt)

    def GUI_info(self):
        tk.Label(self.frame_right_info, text="Face Register", font=self.font_title).grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="FPS: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_fps_info.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, text="Faces in database: ").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_cnt_face_in_database.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, text="Faces in current frame: ").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.label_warning.grid(row=4, column=0, columnspan=4, sticky=tk.W, padx=5, pady=2)
        self.capture_prompt_label.grid(row=5, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 1: Clear all existing face photos").grid(row=6, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)
        tk.Button(self.frame_right_info, text='Clear All Data', command=self.GUI_clear_data, bg='red', fg='white').grid(row=7, column=0, columnspan=4, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 2: Enter Student Details").grid(row=8, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        tk.Label(self.frame_right_info, text="Roll No.: ").grid(row=9, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_rollno.grid(row=9, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Label(self.frame_right_info, text="Name: ").grid(row=10, column=0, sticky=tk.W, padx=5, pady=0)
        self.input_name.grid(row=10, column=1, sticky=tk.W, padx=0, pady=2)

        tk.Button(self.frame_right_info, text='Create Folder', command=self.GUI_get_input_data, bg='lightgreen').grid(row=10, column=2, padx=5)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 3: Auto Capture Face Images (50 images)").grid(row=11, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        tk.Button(self.frame_right_info, text='Start Auto Capture', command=self.start_auto_capture, bg='lightblue').grid(row=12, column=0, columnspan=2, sticky=tk.W)

        self.resume_capture_button = tk.Button(self.frame_right_info, text='Resume Capture', command=self.resume_auto_capture, bg='green', fg='white')
        self.resume_capture_button.grid(row=12, column=2, columnspan=2, sticky=tk.W, padx=5)
        self.resume_capture_button.grid_remove()

        tk.Button(self.frame_right_info, text='Halt Program', command=self.halt_program, bg='red', fg='white').grid(row=13, column=0, columnspan=4, sticky=tk.W, padx=5, pady=20)

        self.log_all.grid(row=14, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        self.frame_right_info.pack(side=tk.RIGHT, padx=10, pady=10)

    def pre_work_mkdir(self):
        os.makedirs(self.path_photos_from_camera, exist_ok=True)

    def check_existing_faces_cnt(self):
        if os.path.isdir(self.path_photos_from_camera) and os.listdir(self.path_photos_from_camera):
            person_list = os.listdir(self.path_photos_from_camera)
            person_num_list = []
            for person in person_list:
                parts = person.split('_')
                if parts and parts[0].isdigit():
                    person_num_list.append(int(parts[0]))
            if person_num_list:
                self.existing_faces_cnt = max(person_num_list)
            else:
                self.existing_faces_cnt = len(person_list)
        else:
            self.existing_faces_cnt = 0

    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        if self.frame_time > 0:
            self.fps = 1.0 / self.frame_time
        self.frame_start_time = now
        self.label_fps_info["text"] = str(round(self.fps, 2))

    def halt_program(self):
        logging.info("Halting the program.")
        try:
            if self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        try:
            self.log_all["text"] = "Extracting features to CSV (efficient mode)..."
            self.win.update_idletasks()
            subprocess.run(["python", "features_extraction_to_csv.py"], check=True)
            self.log_all["text"] = "Features extracted and program halted."
        except subprocess.CalledProcessError as e:
            self.log_all["text"] = f"Error during feature extraction: {e}"
            logging.error(f"Error during feature extraction: {e}")
        finally:
            self.win.destroy()

    def insert_student_to_db(self, roll_no, name):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO students (roll_no, name) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE name = VALUES(name)",
                (roll_no, name)
            )
            conn.commit()
            cur.close()
            conn.close()
            logging.info(f"Student {roll_no} - {name} inserted/updated in DB.")
        except mysql.connector.Error as e:
            logging.error(f"Error inserting student into DB: {e}")

    def create_face_folder(self):
        if not self.input_rollno_char or not self.input_name_char:
            self.log_all["text"] = "Error: Roll Number and Name cannot be empty."
            return

        self.current_face_dir = os.path.join(
            self.path_photos_from_camera,
            f"{self.input_rollno_char}_{self.input_name_char.replace(' ', '_')}"
        )

        if os.path.exists(self.current_face_dir):
            messagebox.showwarning(
                "Folder Exists",
                f"Folder for {self.input_rollno_char}_{self.input_name_char} already exists. Please choose a different Roll Number or clear data."
            )
            self.face_folder_created_flag = False
            return

        try:
            os.makedirs(self.current_face_dir)
            self.log_all[
                "text"] = f"Folder \"{self.current_face_dir}/\" created for {self.input_name_char} (Roll No: {self.input_rollno_char})!"
            logging.info("Create folders: %s", self.current_face_dir)
            self.ss_cnt = 0
            self.face_folder_created_flag = True
            self.capture_prompt_label["text"] = ""

            # 🚀 Insert into MySQL students table
            self.insert_student_to_db(self.input_rollno_char, self.input_name_char)

        except Exception as e:
            self.log_all["text"] = f"Error creating folder: {e}"
            logging.error(f"Error creating folder: {e}")
            self.face_folder_created_flag = False

    def start_auto_capture(self):
        if not self.face_folder_created_flag:
            self.log_all["text"] = "Please create a face folder first (Step 2)."
            return
        if self.capturing_images:
            self.log_all["text"] = "Image capture is already in progress."
            return

        self.capturing_images = True
        self.capture_paused = False
        self.capture_category_index = 0
        self.images_captured_in_category = 0
        self.ss_cnt = 0

        self.show_command_and_pause()

    def show_command_and_pause(self):
        if self.capture_category_index < len(self.capture_categories):
            current_category = self.capture_categories[self.capture_category_index]
            self.capture_prompt_label["text"] = f"GET READY: {current_category.upper()}!"
            self.capture_prompt_label["fg"] = "red"
            self.play_beep_sound()
            self.resume_capture_button.grid()
            self.capture_paused = True
            self.log_all["text"] = f"Position yourself for '{current_category}' and click 'Resume Capture' when ready."
        else:
            self.log_all["text"] = "All image categories captured!"
            self.capture_prompt_label["text"] = "Capture Complete!"
            self.capture_prompt_label["fg"] = "green"
            self.capturing_images = False
            self.resume_capture_button.grid_remove()

    def resume_auto_capture(self):
        if not self.capturing_images or not self.capture_paused:
            return

        self.capture_paused = False
        self.resume_capture_button.grid_remove()

        current_category = self.capture_categories[self.capture_category_index]
        self.capture_prompt_label["text"] = f"CAPTURING: {current_category}! Hold position..."
        self.capture_prompt_label["fg"] = "blue"
        self.log_all["text"] = f"Capturing {current_category} images... Hold your position!"
        self.auto_capture_loop()

    def auto_capture_loop(self):
        if not self.capturing_images or self.capture_paused:
            return

        if self.capture_category_index < len(self.capture_categories):
            current_category = self.capture_categories[self.capture_category_index]
            self.capture_prompt_label["text"] = f"CAPTURING: {current_category}! ({self.images_captured_in_category + 1}/{self.num_images_per_category})"

            if self.current_frame_faces_cnt == 1 and not self.out_of_range_flag and self.current_frame is not None:
                self.ss_cnt += 1
                self.images_captured_in_category += 1

                # Extract ROI safely using slicing and pad if needed
                h_start = max(0, self.face_ROI_height_start - self.hh)
                w_start = max(0, self.face_ROI_width_start - self.ww)
                h_end = min(self.current_frame.shape[0], self.face_ROI_height_start + self.face_ROI_height + self.hh)
                w_end = min(self.current_frame.shape[1], self.face_ROI_width_start + self.face_ROI_width + self.ww)

                roi = self.current_frame[h_start:h_end, w_start:w_end].copy()

                # If roi is too small for intended size, pad it with black pixels
                desired_h = int(self.face_ROI_height * 2) if self.face_ROI_height > 0 else roi.shape[0]
                desired_w = int(self.face_ROI_width * 2) if self.face_ROI_width > 0 else roi.shape[1]
                if roi.shape[0] < desired_h or roi.shape[1] < desired_w:
                    pad_h = max(0, desired_h - roi.shape[0])
                    pad_w = max(0, desired_w - roi.shape[1])
                    roi = np.pad(roi, ((0, pad_h), (0, pad_w), (0, 0)), mode='constant', constant_values=0)

                filename = os.path.join(self.current_face_dir, f"{current_category.replace(' ', '_').lower()}_{self.images_captured_in_category}.jpg")
                # roi is RGB already
                cv2.imwrite(filename, cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))
                self.log_all["text"] = f"Captured {current_category} image {self.images_captured_in_category}/{self.num_images_per_category} for {self.input_name_char}!"
                logging.info("Save into： %s", filename)

            # Check if category is complete
            if self.images_captured_in_category >= self.num_images_per_category:
                self.capture_category_index += 1
                self.images_captured_in_category = 0

                if self.capture_category_index < len(self.capture_categories):
                    self.log_all["text"] = f"Category '{current_category}' complete! Preparing next command..."
                    self.win.after(1000, self.show_command_and_pause)
                    return
                else:
                    self.show_command_and_pause()
                    return

            self.win.after(self.capture_delay_ms, self.auto_capture_loop)
        else:
            self.log_all["text"] = "All image categories captured!"
            self.capture_prompt_label["text"] = "Capture Complete!"
            self.capture_prompt_label["fg"] = "green"
            self.capturing_images = False
            self.resume_capture_button.grid_remove()

    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    logging.error("Failed to read frame from camera.")
                    return False, None
                frame = cv2.resize(frame, (640, 480))
                # Convert to RGB for PIL/Tkinter display
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return False, None
        except Exception as e:
            logging.error(f"Error getting frame: {e}")
            messagebox.showerror("Camera Error", f"Error accessing camera: {e}")
            self.halt_program()
            return False, None

    def process(self):
        ret, self.current_frame = self.get_frame()
        if not ret or self.current_frame is None:
            self.win.after(20, self.process)
            return

        faces = detector(self.current_frame, 0)

        self.update_fps()
        self.label_face_cnt["text"] = str(len(faces))

        if len(faces) != 0:
            d = faces[0]
            self.face_ROI_width_start = d.left()
            self.face_ROI_height_start = d.top()
            self.face_ROI_height = (d.bottom() - d.top())
            self.face_ROI_width = (d.right() - d.left())
            self.hh = int(self.face_ROI_height / 2)
            self.ww = int(self.face_ROI_width / 2)

            if (d.right() + self.ww) > 640 or (d.bottom() + self.hh > 480) or (d.left() - self.ww < 0) or (d.top() - self.hh < 0):
                self.label_warning["text"] = "OUT OF RANGE"
                self.label_warning['fg'] = 'red'
                self.out_of_range_flag = True
                color_rectangle = (255, 0, 0)
            else:
                self.out_of_range_flag = False
                self.label_warning["text"] = ""
                color_rectangle = (255, 255, 255)

            # Draw rectangle on a copy for display
            display = self.current_frame.copy()
            x1 = max(0, d.left() - self.ww)
            y1 = max(0, d.top() - self.hh)
            x2 = min(self.current_frame.shape[1], d.right() + self.ww)
            y2 = min(self.current_frame.shape[0], d.bottom() + self.hh)
            display = cv2.rectangle(display, (x1, y1), (x2, y2), color_rectangle, 2)
        else:
            self.label_warning["text"] = "No face detected"
            self.label_warning['fg'] = 'orange'
            self.out_of_range_flag = True
            display = self.current_frame.copy()

        self.current_frame_faces_cnt = len(faces)

        # Convert to PIL Image for Tkinter
        img_Image = Image.fromarray(display)
        img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
        self.label.img_tk = img_PhotoImage
        self.label.configure(image=img_PhotoImage)

        self.win.after(20, self.process)

    def run(self):
        self.pre_work_mkdir()
        self.check_existing_faces_cnt()
        self.GUI_info()
        self.process()
        self.win.mainloop()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    Face_Register_con = Face_Register()
    Face_Register_con.run()


if __name__ == '__main__':
    main()