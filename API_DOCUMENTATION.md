(cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF'
diff --git a/API_DOCUMENTATION.md b/API_DOCUMENTATION.md
--- a/API_DOCUMENTATION.md
+++ b/API_DOCUMENTATION.md
@@ -0,0 +1,426 @@
+# Facial Recognition Attendance System - API Documentation
+
+## Table of Contents
+1. [Overview](#overview)
+2. [Core Classes](#core-classes)
+3. [Web Application API](#web-application-api)
+4. [Face Registration System](#face-registration-system)
+5. [Face Recognition System](#face-recognition-system)
+6. [Feature Extraction System](#feature-extraction-system)
+7. [Database Schema](#database-schema)
+8. [Usage Examples](#usage-examples)
+9. [Error Handling](#error-handling)
+10. [Configuration](#configuration)
+
+## Overview
+
+The Facial Recognition Attendance System is a comprehensive Python application that provides face registration, real-time recognition, and attendance tracking capabilities. The system consists of several interconnected components:
+
+- **Face Registration Module** (`main.py`): Captures and stores face images
+- **Face Recognition Module** (`attendance_taker.py`): Recognizes faces and logs attendance
+- **Feature Extraction Module** (`features_extraction_to_csv.py`): Extracts facial features for recognition
+- **Web Interface** (`app.py`): Provides attendance viewing capabilities
+
+## Core Classes
+
+### Face_Register Class (`main.py`)
+
+The main class for face registration and image capture.
+
+#### Constructor
+```python
+def __init__(self):
+```
+**Purpose**: Initializes the face registration system with GUI components and camera setup.
+
+**Attributes**:
+- `current_frame_faces_cnt`: Number of faces detected in current frame
+- `existing_faces_cnt`: Number of faces already in database
+- `ss_cnt`: Screenshot counter
+- `win`: Tkinter main window
+- `cap`: OpenCV video capture object
+- `path_photos_from_camera`: Directory path for storing face images
+
+#### Public Methods
+
+##### `run()`
+```python
+def run(self):
+```
+**Purpose**: Starts the face registration application.
+**Returns**: None
+**Usage**:
+```python
+face_register = Face_Register()
+face_register.run()
+```
+
+##### `GUI_clear_data()`
+```python
+def GUI_clear_data(self):
+```
+**Purpose**: Clears all existing face data and resets the system.
+**Returns**: None
+**Side Effects**: 
+- Removes all face folders from `data/data_faces_from_camera/`
+- Deletes `data/features_all.csv`
+- Resets face counter to 0
+
+##### `GUI_get_input_name()`
+```python
+def GUI_get_input_name(self):
+```
+**Purpose**: Retrieves the name input from GUI and creates face folder.
+**Returns**: None
+**Side Effects**: Creates a new folder for the person's face images
+
+##### `save_current_face()`
+```python
+def save_current_face(self):
+```
+**Purpose**: Saves the currently detected face as an image.
+**Returns**: None
+**Side Effects**: Saves face image to the current person's folder
+
+##### `halt_program()`
+```python
+def halt_program(self):
+```
+**Purpose**: Safely stops the application and runs feature extraction.
+**Returns**: None
+**Side Effects**: 
+- Releases camera resources
+- Runs `features_extraction_to_csv.py`
+- Closes GUI window
+
+### Face_Recognizer Class (`attendance_taker.py`)
+
+The main class for face recognition and attendance logging.
+
+#### Constructor
+```python
+def __init__(self):
+```
+**Purpose**: Initializes the face recognition system with tracking capabilities.
+
+**Key Attributes**:
+- `face_features_known_list`: List of known face features
+- `face_name_known_list`: List of known face names
+- `current_frame_face_cnt`: Number of faces in current frame
+- `reclassify_interval`: Frames between reclassification attempts
+
+#### Public Methods
+
+##### `run()`
+```python
+def run(self):
+```
+**Purpose**: Starts the face recognition and attendance system.
+**Returns**: None
+**Usage**:
+```python
+recognizer = Face_Recognizer()
+recognizer.run()
+```
+
+##### `get_face_database()`
+```python
+def get_face_database(self):
+```
+**Purpose**: Loads known faces from `data/features_all.csv`.
+**Returns**: 
+- `1` if database loaded successfully
+- `0` if database file not found
+**Side Effects**: Populates `face_features_known_list` and `face_name_known_list`
+
+##### `attendance(name)`
+```python
+def attendance(self, name):
+```
+**Purpose**: Records attendance for a recognized person.
+**Parameters**:
+- `name` (str): Name of the person to mark as present
+**Returns**: None
+**Side Effects**: Inserts attendance record into SQLite database
+
+##### `process(stream)`
+```python
+def process(self, stream):
+```
+**Purpose**: Main processing loop for face detection and recognition.
+**Parameters**:
+- `stream`: OpenCV video capture object
+**Returns**: None
+**Side Effects**: 
+- Detects faces in video stream
+- Recognizes known faces
+- Logs attendance for recognized persons
+- Displays recognition results
+
+#### Static Methods
+
+##### `return_euclidean_distance(feature_1, feature_2)`
+```python
+@staticmethod
+def return_euclidean_distance(feature_1, feature_2):
+```
+**Purpose**: Calculates Euclidean distance between two 128D feature vectors.
+**Parameters**:
+- `feature_1` (numpy.ndarray): First feature vector
+- `feature_2` (numpy.ndarray): Second feature vector
+**Returns**: `float`: Euclidean distance between the features
+
+## Web Application API (`app.py`)
+
+### Flask Routes
+
+#### `index()`
+```python
+@app.route('/')
+def index():
+```
+**Purpose**: Serves the main attendance viewing page.
+**Returns**: Rendered `index.html` template
+**Template Variables**:
+- `selected_date`: Currently selected date (empty string initially)
+- `no_data`: Boolean indicating if no data is available
+
+#### `attendance()`
+```python
+@app.route('/attendance', methods=['POST'])
+def attendance():
+```
+**Purpose**: Handles attendance data requests for specific dates.
+**HTTP Method**: POST
+**Form Parameters**:
+- `selected_date`: Date in YYYY-MM-DD format
+**Returns**: Rendered `index.html` template with attendance data
+**Template Variables**:
+- `selected_date`: The requested date
+- `attendance_data`: List of (name, time) tuples
+- `no_data`: Boolean indicating if no data is available
+
+## Feature Extraction System (`features_extraction_to_csv.py`)
+
+### Public Functions
+
+#### `return_128d_features(path_img)`
+```python
+def return_128d_features(path_img):
+```
+**Purpose**: Extracts 128-dimensional feature vector from a face image.
+**Parameters**:
+- `path_img` (str): Path to the image file
+**Returns**: 
+- `numpy.ndarray`: 128D feature vector if face detected
+- `0`: If no face detected in image
+**Usage**:
+```python
+features = return_128d_features("path/to/face.jpg")
+if features != 0:
+    print("Face features extracted successfully")
+```
+
+#### `return_features_mean_personX(path_face_personX)`
+```python
+def return_features_mean_personX(path_face_personX):
+```
+**Purpose**: Calculates mean feature vector for all images of a person.
+**Parameters**:
+- `path_face_personX` (str): Path to folder containing person's face images
+**Returns**: `numpy.ndarray`: Mean 128D feature vector for the person
+**Usage**:
+```python
+mean_features = return_features_mean_personX("data/data_faces_from_camera/person_1_john")
+```
+
+#### `main()`
+```python
+def main():
+```
+**Purpose**: Main function that processes all registered faces and creates features CSV.
+**Returns**: None
+**Side Effects**: Creates `data/features_all.csv` with all face features
+
+## Database Schema
+
+### SQLite Database: `attendance.db`
+
+#### Table: `attendance`
+```sql
+CREATE TABLE attendance (
+    name TEXT,
+    time TEXT,
+    date DATE,
+    UNIQUE(name, date)
+);
+```
+
+**Columns**:
+- `name`: Person's name (TEXT)
+- `time`: Attendance time in HH:MM:SS format (TEXT)
+- `date`: Attendance date in YYYY-MM-DD format (DATE)
+- `UNIQUE(name, date)`: Prevents duplicate attendance records per person per day
+
+## Usage Examples
+
+### 1. Registering New Faces
+
+```python
+# Start the face registration system
+python main.py
+
+# Follow the GUI instructions:
+# 1. Click "Clear" to remove old data
+# 2. Enter the person's name
+# 3. Click "Input" to create folder
+# 4. Click "Save current face" to capture face images
+# 5. Click "HLT" to stop and extract features
+```
+
+### 2. Taking Attendance
+
+```python
+# Start the attendance system
+python attendance_taker.py
+
+# The system will:
+# 1. Load known faces from features_all.csv
+# 2. Start video capture
+# 3. Detect and recognize faces in real-time
+# 4. Log attendance for recognized persons
+# 5. Press 'q' to quit
+```
+
+### 3. Viewing Attendance Records
+
+```python
+# Start the web application
+python app.py
+
+# Open browser to http://localhost:5000
+# Select a date to view attendance records
+```
+
+### 4. Feature Extraction
+
+```python
+# Extract features from all registered faces
+python features_extraction_to_csv.py
+
+# This creates data/features_all.csv with all face features
+```
+
+## Error Handling
+
+### Common Issues and Solutions
+
+#### 1. Camera Not Found
+```python
+# Error: "Error: No video input!!!"
+# Solution: Ensure camera is connected and not in use by another application
+```
+
+#### 2. Dlib Model Files Missing
+```python
+# Error: "shape_predictor_68_face_landmarks.dat not found"
+# Solution: Download required Dlib model files from the provided Google Drive link
+```
+
+#### 3. No Faces Detected
+```python
+# Error: "No face in current frame!"
+# Solution: Ensure good lighting and face is clearly visible to camera
+```
+
+#### 4. Database Connection Issues
+```python
+# Error: "database is locked"
+# Solution: Ensure no other process is accessing the database file
+```
+
+### Logging Levels
+
+The system uses Python's logging module with configurable levels:
+
+```python
+# Debug level (detailed frame-by-frame info)
+logging.basicConfig(level=logging.DEBUG)
+
+# Info level (standard operation info)
+logging.basicConfig(level=logging.INFO)
+```
+
+## Configuration
+
+### File Structure
+```
+project/
+├── main.py                          # Face registration
+├── attendance_taker.py              # Face recognition
+├── features_extraction_to_csv.py    # Feature extraction
+├── app.py                          # Web interface
+├── attendance.db                   # SQLite database
+├── data/
+│   ├── data_faces_from_camera/     # Face images
+│   ├── data_dlib/                  # Dlib model files
+│   └── features_all.csv           # Face features
+├── templates/
+│   └── index.html                 # Web template
+└── requirements.txt               # Python dependencies
+```
+
+### Required Dependencies
+
+```txt
+dlib
+opencv-python
+numpy
+pandas
+flask
+pillow
+```
+
+### Environment Variables
+
+No environment variables are required, but the following directories must exist:
+- `data/data_faces_from_camera/`
+- `data/data_dlib/`
+
+### Performance Considerations
+
+1. **Face Detection Threshold**: 0.4 (Euclidean distance)
+2. **Reclassification Interval**: 10 frames
+3. **Video Resolution**: 640x480
+4. **FPS Display**: Updates every second
+
+### Security Notes
+
+1. **Face Data**: Stored locally in `data/` directory
+2. **Database**: SQLite file with no encryption
+3. **Web Interface**: No authentication required
+4. **Camera Access**: Requires user permission
+
+## API Versioning
+
+Current Version: 1.0.0
+
+### Breaking Changes
+- None in current version
+
+### Deprecated Features
+- None in current version
+
+## Contributing
+
+When contributing to this project:
+
+1. Follow the existing code structure
+2. Add appropriate logging statements
+3. Update this documentation for new features
+4. Test with both debug and info logging levels
+5. Ensure backward compatibility
+
+## License
+
+This project is licensed under the MIT License. See LICENSE file for details.
EOF
)
