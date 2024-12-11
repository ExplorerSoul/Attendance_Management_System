# Attendance_Management_System
# Facial Recognition Attendance Management System

## Overview

The Facial Recognition Attendance Management System is a Python-based application that automates the process of taking attendance using facial recognition technology. The system captures images of students, encodes their faces, and recognizes them in real-time during attendance sessions. It records attendance in both a MySQL database and CSV files for easy access and management.

## Features

- **Image Capture**: Capture multiple images (up to 140) for each student to create a robust dataset.
- **Face Recognition**: Recognize students in real-time using webcam input.
- **Attendance Recording**: Store attendance records in a MySQL database and save them in subject-specific CSV files.
- **Duplicate Handling**: Manage duplicate entries in the database by updating existing records instead of inserting new ones.

## Requirements

- Python 3.x
- OpenCV
- dlib
- face_recognition
- mysql-connector-python
- numpy
- pandas
- tkinter (for GUI)

## Installation

1. Clone the repository:

   ```bash
   git clone <https://github.com/ExplorerSoul/Attendance_Management_System>
## Install the required libraries:
   ```bash
   pip install opencv-python dlib face_recognition mysql-connector-python numpy pandas
   ```
### Set up your MySQL database:
# Create a database named attendance_management_system.
Create the necessary tables (users and attendance) with appropriate fields.

### Usage
Prepare Training Data:
Place student images in the TrainingImages folder, organized by student ID (e.g., folders named 1, 2, etc.).
Each folder should contain images of the respective student.

## Run the Application:
1) Open a terminal or command prompt.
Navigate to the project directory and run:
   ```bash
   python attendance_system.py
   ```
2) Capture Images:
When prompted, enter the enrollment ID and name of the student to capture their images.
The application will capture up to 140 images for each student.
3) Take Attendance:
When prompted, enter the subject name for attendance.

The application will start recognizing faces from the webcam feed and log attendance accordingly.
4) Viewing Attendance Records:
Attendance records are saved in CSV files located in the attendance folder, named according to the subject (e.g., attendance_math.csv).
### Troubleshooting
If you encounter issues with unsupported image types, ensure that all images are in JPEG or PNG format.
If you experience performance issues with the camera, ensure that no other applications are using the webcam simultaneously.
