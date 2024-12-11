import os
import cv2
import datetime
import dlib
import face_recognition
import numpy as np
import mysql.connector
import pickle
import csv
import tkinter as tk
from tkinter import messagebox, simpledialog
import traceback

def ensure_rgb_image(image):
    """
    Ensure the image is in RGB format.
    
    Args:
        image (numpy.ndarray): Input image
    
    Returns:
        numpy.ndarray: RGB image
    """
    # If image is grayscale, convert to RGB
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    # If image has 4 channels (RGBA), convert to RGB
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    # If image is not 3 channels, raise an error
    if image.shape[2] != 3:
        raise ValueError("Image must be 3-channel RGB")
    
    return image

def take_img(enrollment, name):
    """Capture images from webcam and save them in a specified directory."""
    if enrollment == '' or name == '':
        print("Please fill in all fields!")
        return
    
    try:
        base_dir = 'TrainingImage'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        enrollment_dir = os.path.join(base_dir, enrollment)
        if not os.path.exists(enrollment_dir):
            os.makedirs(enrollment_dir)

        cam = cv2.VideoCapture(0)
        detector = dlib.get_frontal_face_detector()
        
        sampleNum = 0
        
        print("Starting image capture. Press 'q' to quit.")
        
        while True:
            ret, img = cam.read()
            
            if not ret:
                print("Failed to capture image from webcam.")
                break
            
            # Convert image to RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = detector(rgb_img)
            
            for face in faces:
                x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                
                # Extract face region
                face_image = rgb_img[y:y+h, x:x+w]
                
                # Ensure image is 3 channels
                if face_image.ndim == 2:
                    face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
                elif face_image.shape[2] == 4:
                    face_image = cv2.cvtColor(face_image, cv2.COLOR_RGBA2RGB)
                
                # Draw rectangle on original image
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                sampleNum += 1
                
                # Save image (convert back to BGR for OpenCV save)
                cv2.imwrite(f"{enrollment_dir}/{name}.{enrollment}.{sampleNum}.jpg", 
                            cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))
                
                print(f"Image {sampleNum} saved for Enrollment: {enrollment}, Name: {name}")
                
            cv2.imshow('Frame', img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if sampleNum >= 140:  # Capture up to 140 images per student
                break

        cam.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error details: {traceback.format_exc()}")  # Add detailed error traceback

def prepare_training_data(data_folder_path):
    """Prepare training data by loading images and extracting face encodings."""
    encodings = []
    labels = []
    
    for dir_name in os.listdir(data_folder_path):
        if not dir_name.startswith('.'):
            label = dir_name  # Assuming dir_name is the enrollment ID
            subject_dir_path = os.path.join(data_folder_path, dir_name)
            
            for image_name in os.listdir(subject_dir_path):
                if image_name.endswith(".jpg"):
                    image_path = os.path.join(subject_dir_path, image_name)
                    
                    # Read the image using OpenCV
                    image = cv2.imread(image_path)
                    
                    # Convert to RGB
                    rgb_image = ensure_rgb_image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    
                    # Extract face encodings
                    encoding = face_recognition.face_encodings(rgb_image)
                    
                    if encoding:
                        encodings.append(encoding[0])  # Take the first encoding
                        labels.append(label)  # Use the student ID as the name
    
    return encodings, labels


def test_model(encodings, names):
    """Test the model by capturing images from webcam and recognizing faces."""
    cam = cv2.VideoCapture(0)
    
    while True:
        ret, img = cam.read()
        
        if not ret:
            print("Failed to capture image from webcam.")
            break
        
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(encodings, face_encoding)
            
            label_text = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                label_text = names[first_match_index]  # Use actual student ID
                
                # Record attendance in the database and CSV file
                record_attendance(names[first_match_index], label_text)

            cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.putText(img, label_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        cv2.imshow('Face Recognition', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()

def record_attendance(enrollment_id, name):
    """Record attendance in the MySQL database and save it to a CSV file."""
    date_today = datetime.datetime.now().date()  # Get today's date
    time_now = datetime.datetime.now().time()     # Get current time
    
    connection = connect_to_database()
    
    if connection:
        cursor = connection.cursor()
        
        # Use INSERT ... ON DUPLICATE KEY UPDATE to handle duplicates
        sql_query = """
        INSERT INTO attendance (id, name, date, time) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE time=VALUES(time);
        """
        
        cursor.execute(sql_query,
                       (enrollment_id,
                        name,
                        date_today.strftime('%Y-%m-%d'),
                        time_now.strftime('%H:%M:%S')))
        
        connection.commit()  # Commit changes to the database
        
        cursor.close()
        connection.close()
        
        print(f"Attendance recorded for Student ID: {enrollment_id} ({name}) on {date_today} at {time_now}")

    # Save attendance to CSV file based on subject name
    save_attendance_to_csv(enrollment_id, name)

def save_attendance_to_csv(enrollment_id, name):
    """Save attendance record to a CSV file based on subject."""
    subject_name = input("Enter Subject Name for Attendance: ")   # Ask for subject name each time attendance is recorded.
    
    attendance_folder = 'attendance'
    
    # Create attendance folder if it doesn't exist
    if not os.path.exists(attendance_folder):
        os.makedirs(attendance_folder)

    csv_file_path = os.path.join(attendance_folder, f'attendance_{subject_name}.csv')

    # Check if the CSV file exists to determine whether to write headers or not
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['ID', 'Name', 'Date', 'Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only once
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'ID': enrollment_id,
            'Name': name,
            'Date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'Time': datetime.datetime.now().strftime('%H:%M:%S')
        })

def create_gui():
    """Create an integrated GUI for taking images and recording attendance."""
    
    def take_images():
        """Handle taking images."""
        enrollment_id = enrollment_entry.get().strip()
        name_entry_val = name_entry.get().strip()
        
        if not enrollment_id or not name_entry_val:
            messagebox.showerror("Error", "Please enter Enrollment ID and Name")
            return
        
        take_img(enrollment_id, name_entry_val)
        messagebox.showinfo("Success", "Images captured successfully!")
    
    def take_attendance():
        """Handle taking attendance."""
        encodings_file = "encodings.pickle"
        
        try:
            print("Loading training data...")
            
            encodings, names = load_encodings(encodings_file)
            
            if encodings is None or names is None:
                print("No saved encodings found. Training new data...")
                encode_faces("TrainingImage")  # Train and save new encodings
                encodings, names = load_encodings(encodings_file)  # Load newly trained data
            
            print("Starting face recognition...")
            test_model(encodings, names)
            
            messagebox.showinfo("Attendance", "Attendance process completed!")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Create main window
    root = tk.Tk()
    root.title("Attendance Management System")
    root.geometry("400x450")  # Set a fixed window size
    root.configure(bg='#f0f0f0')  # Light gray background
    
    # Create a frame for the entire content
    main_frame = tk.Frame(root, bg='#f0f0f0')
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, text="Attendance Management System", 
                            font=("Helvetica", 16, "bold"), 
                            bg='#f0f0f0')
    title_label.pack(pady=(0,20))
    
    # Enrollment ID Entry
    enrollment_label = tk.Label(main_frame, text="Enrollment ID:", bg='#f0f0f0')
    enrollment_label.pack()
    enrollment_entry = tk.Entry(main_frame, width=30)
    enrollment_entry.pack(pady=(0,10))
    
    # Name Entry
    name_label = tk.Label(main_frame, text="Name:", bg='#f0f0f0')
    name_label.pack()
    name_entry = tk.Entry(main_frame, width=30)
    name_entry.pack(pady=(0,20))
    
    # Button Frame to center buttons
    button_frame = tk.Frame(main_frame, bg='#f0f0f0')
    button_frame.pack(expand=True)
    
    # Take Images Button
    take_images_btn = tk.Button(
        button_frame, 
        text="Take Images", 
        command=take_images,
        width=20,  # Medium-sized button
        height=2,
        bg='#4CAF50',  # Green color
        fg='white',
        font=("Helvetica", 10)
    )
    take_images_btn.pack(pady=10)
    
    # Take Attendance Button
    take_attendance_btn = tk.Button(
        button_frame, 
        text="Take Attendance", 
        command=take_attendance,
        width=20,  # Medium-sized button
        height=2,
        bg='#2196F3',  # Blue color
        fg='white',
        font=("Helvetica", 10)
    )
    take_attendance_btn.pack(pady=10)
    
    root.mainloop()

# Ensure the rest of your existing functions (take_img, test_model, etc.) remain the same

if __name__ == "__main__":
   create_gui()