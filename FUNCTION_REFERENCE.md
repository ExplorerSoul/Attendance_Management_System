# Function Reference - Facial Recognition Attendance System

## Table of Contents
1. [Face Registration Functions](#face-registration-functions)
2. [Face Recognition Functions](#face-recognition-functions)
3. [Feature Extraction Functions](#feature-extraction-functions)
4. [Web Application Functions](#web-application-functions)
5. [Utility Functions](#utility-functions)

---

## Face Registration Functions

### Class: Face_Register

#### `__init__()`
**File**: `main.py`  
**Line**: 15  
**Signature**: `def __init__(self):`  
**Purpose**: Initializes the face registration system with GUI components and camera setup.  
**Returns**: None  
**Side Effects**: 
- Creates Tkinter window
- Initializes OpenCV video capture
- Sets up GUI components
- Creates data directories

**Usage**:
```python
register = Face_Register()
```

#### `run()`
**File**: `main.py`  
**Line**: 295  
**Signature**: `def run(self):`  
**Purpose**: Starts the face registration application and enters the main event loop.  
**Returns**: None  
**Side Effects**: 
- Creates necessary directories
- Sets up GUI
- Starts video processing loop
- Enters Tkinter mainloop

**Usage**:
```python
register = Face_Register()
register.run()
```

#### `GUI_clear_data()`
**File**: `main.py`  
**Line**: 75  
**Signature**: `def GUI_clear_data(self):`  
**Purpose**: Clears all existing face data and resets the system to initial state.  
**Returns**: None  
**Side Effects**: 
- Removes all folders from `data/data_faces_from_camera/`
- Deletes `data/features_all.csv` if it exists
- Resets `existing_faces_cnt` to 0
- Updates GUI display

**Usage**:
```python
register.GUI_clear_data()
```

#### `GUI_get_input_name()`
**File**: `main.py`  
**Line**: 82  
**Signature**: `def GUI_get_input_name(self):`  
**Purpose**: Retrieves the name input from GUI and creates a folder for the person's face images.  
**Returns**: None  
**Side Effects**: 
- Creates new folder in `data/data_faces_from_camera/`
- Updates `existing_faces_cnt`
- Updates GUI display

**Usage**:
```python
register.GUI_get_input_name()
```

#### `save_current_face()`
**File**: `main.py`  
**Line**: 150  
**Signature**: `def save_current_face(self):`  
**Purpose**: Saves the currently detected face as an image file.  
**Returns**: None  
**Side Effects**: 
- Saves face image to current person's folder
- Updates screenshot counter
- Logs the save operation

**Prerequisites**: 
- Face folder must be created
- Exactly one face must be detected in current frame
- Face must be within camera range

**Usage**:
```python
register.save_current_face()
```

#### `halt_program()`
**File**: `main.py`  
**Line**: 140  
**Signature**: `def halt_program(self):`  
**Purpose**: Safely stops the application and runs feature extraction before closing.  
**Returns**: None  
**Side Effects**: 
- Releases camera resources
- Runs `features_extraction_to_csv.py` as subprocess
- Closes Tkinter window

**Usage**:
```python
register.halt_program()
```

#### `update_fps()`
**File**: `main.py`  
**Line**: 120  
**Signature**: `def update_fps(self):`  
**Purpose**: Updates and displays the current FPS (frames per second) of the video stream.  
**Returns**: None  
**Side Effects**: 
- Updates `fps` and `fps_show` attributes
- Updates FPS display in GUI

**Usage**:
```python
register.update_fps()
```

#### `create_face_folder()`
**File**: `main.py`  
**Line**: 165  
**Signature**: `def create_face_folder(self):`  
**Purpose**: Creates a new folder for storing a person's face images.  
**Returns**: None  
**Side Effects**: 
- Creates directory in `data/data_faces_from_camera/`
- Updates `existing_faces_cnt`
- Sets `current_face_dir`
- Resets screenshot counter

**Usage**:
```python
register.create_face_folder()
```

#### `get_frame()`
**File**: `main.py`  
**Line**: 200  
**Signature**: `def get_frame(self):`  
**Purpose**: Captures a frame from the video stream and converts it to RGB format.  
**Returns**: 
- `tuple`: (ret, frame) where ret is boolean success flag and frame is numpy array
**Side Effects**: None

**Usage**:
```python
ret, frame = register.get_frame()
if ret:
    # Process frame
```

#### `process()`
**File**: `main.py`  
**Line**: 210  
**Signature**: `def process(self):`  
**Purpose**: Main processing loop for face detection and GUI updates.  
**Returns**: None  
**Side Effects**: 
- Detects faces in current frame
- Updates GUI with face count and FPS
- Draws rectangles around detected faces
- Updates display image

**Usage**:
```python
register.process()
```

---

## Face Recognition Functions

### Class: Face_Recognizer

#### `__init__()`
**File**: `attendance_taker.py`  
**Line**: 35  
**Signature**: `def __init__(self):`  
**Purpose**: Initializes the face recognition system with tracking capabilities.  
**Returns**: None  
**Side Effects**: 
- Initializes face tracking lists
- Sets up FPS tracking
- Initializes recognition parameters

**Usage**:
```python
recognizer = Face_Recognizer()
```

#### `run()`
**File**: `attendance_taker.py`  
**Line**: 320  
**Signature**: `def run(self):`  
**Purpose**: Starts the face recognition and attendance system.  
**Returns**: None  
**Side Effects**: 
- Opens video capture
- Starts recognition process
- Releases camera resources on exit

**Usage**:
```python
recognizer = Face_Recognizer()
recognizer.run()
```

#### `get_face_database()`
**File**: `attendance_taker.py`  
**Line**: 75  
**Signature**: `def get_face_database(self):`  
**Purpose**: Loads known faces from the features CSV file.  
**Returns**: 
- `int`: 1 if database loaded successfully, 0 if file not found
**Side Effects**: 
- Populates `face_features_known_list`
- Populates `face_name_known_list`

**Usage**:
```python
if recognizer.get_face_database():
    print("Database loaded successfully")
else:
    print("Database file not found")
```

#### `attendance(name)`
**File**: `attendance_taker.py`  
**Line**: 180  
**Signature**: `def attendance(self, name):`  
**Purpose**: Records attendance for a recognized person in the database.  
**Parameters**: 
- `name` (str): Name of the person to mark as present
**Returns**: None  
**Side Effects**: 
- Inserts attendance record into SQLite database
- Prevents duplicate entries for same person on same date

**Usage**:
```python
recognizer.attendance("John Doe")
```

#### `process(stream)`
**File**: `attendance_taker.py`  
**Line**: 200  
**Signature**: `def process(self, stream):`  
**Purpose**: Main processing loop for face detection, recognition, and attendance logging.  
**Parameters**: 
- `stream`: OpenCV video capture object
**Returns**: None  
**Side Effects**: 
- Detects faces in video stream
- Recognizes known faces
- Logs attendance for recognized persons
- Displays recognition results

**Usage**:
```python
cap = cv2.VideoCapture(0)
recognizer.process(cap)
cap.release()
```

#### `update_fps()`
**File**: `attendance_taker.py`  
**Line**: 95  
**Signature**: `def update_fps(self):`  
**Purpose**: Updates the FPS calculation for the video stream.  
**Returns**: None  
**Side Effects**: 
- Updates `fps` and `fps_show` attributes

**Usage**:
```python
recognizer.update_fps()
```

#### `return_euclidean_distance(feature_1, feature_2)`
**File**: `attendance_taker.py`  
**Line**: 105  
**Signature**: `@staticmethod def return_euclidean_distance(feature_1, feature_2):`  
**Purpose**: Calculates Euclidean distance between two 128D feature vectors.  
**Parameters**: 
- `feature_1` (numpy.ndarray): First 128D feature vector
- `feature_2` (numpy.ndarray): Second 128D feature vector
**Returns**: `float`: Euclidean distance between the features

**Usage**:
```python
distance = Face_Recognizer.return_euclidean_distance(features1, features2)
```

#### `centroid_tracker()`
**File**: `attendance_taker.py`  
**Line**: 115  
**Signature**: `def centroid_tracker(self):`  
**Purpose**: Uses centroid tracking to link faces between consecutive frames.  
**Returns**: None  
**Side Effects**: 
- Updates `current_frame_face_name_list` based on tracking

**Usage**:
```python
recognizer.centroid_tracker()
```

#### `draw_note(img_rd)`
**File**: `attendance_taker.py`  
**Line**: 135  
**Signature**: `def draw_note(self, img_rd):`  
**Purpose**: Draws information overlay on the video frame.  
**Parameters**: 
- `img_rd`: OpenCV image array to draw on
**Returns**: None  
**Side Effects**: 
- Adds text overlay to the image

**Usage**:
```python
recognizer.draw_note(frame)
```

---

## Feature Extraction Functions

### `return_128d_features(path_img)`
**File**: `features_extraction_to_csv.py`  
**Line**: 25  
**Signature**: `def return_128d_features(path_img):`  
**Purpose**: Extracts 128-dimensional feature vector from a face image.  
**Parameters**: 
- `path_img` (str): Path to the image file
**Returns**: 
- `numpy.ndarray`: 128D feature vector if face detected
- `0`: If no face detected in image

**Usage**:
```python
features = return_128d_features("path/to/face.jpg")
if features != 0:
    print("Features extracted:", len(features))
```

### `return_features_mean_personX(path_face_personX)`
**File**: `features_extraction_to_csv.py`  
**Line**: 45  
**Signature**: `def return_features_mean_personX(path_face_personX):`  
**Purpose**: Calculates mean feature vector for all images of a person.  
**Parameters**: 
- `path_face_personX` (str): Path to folder containing person's face images
**Returns**: `numpy.ndarray`: Mean 128D feature vector for the person

**Usage**:
```python
mean_features = return_features_mean_personX("data/data_faces_from_camera/person_1_john")
```

### `main()`
**File**: `features_extraction_to_csv.py`  
**Line**: 65  
**Signature**: `def main():`  
**Purpose**: Main function that processes all registered faces and creates features CSV.  
**Returns**: None  
**Side Effects**: 
- Creates `data/features_all.csv` with all face features
- Processes all folders in `data/data_faces_from_camera/`

**Usage**:
```python
if __name__ == '__main__':
    main()
```

---

## Web Application Functions

### `index()`
**File**: `app.py`  
**Line**: 9  
**Signature**: `@app.route('/') def index():`  
**Purpose**: Serves the main attendance viewing page.  
**Returns**: Rendered `index.html` template  
**Template Variables**: 
- `selected_date`: Currently selected date (empty string initially)
- `no_data`: Boolean indicating if no data is available

**Usage**: Access via web browser at `http://localhost:5000/`

### `attendance()`
**File**: `app.py`  
**Line**: 15  
**Signature**: `@app.route('/attendance', methods=['POST']) def attendance():`  
**Purpose**: Handles attendance data requests for specific dates.  
**HTTP Method**: POST  
**Form Parameters**: 
- `selected_date`: Date in YYYY-MM-DD format
**Returns**: Rendered `index.html` template with attendance data  
**Template Variables**: 
- `selected_date`: The requested date
- `attendance_data`: List of (name, time) tuples
- `no_data`: Boolean indicating if no data is available

**Usage**: Submit form from web interface

---

## Utility Functions

### Database Operations

#### SQLite Connection
**File**: `attendance_taker.py`  
**Line**: 25-30  
**Purpose**: Creates and configures SQLite database connection.  
**Usage**: Automatically executed on module import

#### Table Creation
**File**: `attendance_taker.py`  
**Line**: 32-35  
**Purpose**: Creates attendance table if it doesn't exist.  
**Usage**: Automatically executed on module import

### Logging Functions

#### `logging.basicConfig()`
**Used in**: All modules  
**Purpose**: Configures logging level and format.  
**Usage**:
```python
logging.basicConfig(level=logging.INFO)  # or logging.DEBUG
```

### OpenCV Functions

#### `cv2.VideoCapture()`
**Used in**: `main.py`, `attendance_taker.py`  
**Purpose**: Opens video capture device.  
**Usage**:
```python
cap = cv2.VideoCapture(0)  # 0 for default camera
```

#### `cv2.imshow()`
**Used in**: `attendance_taker.py`  
**Purpose**: Displays video frame in window.  
**Usage**:
```python
cv2.imshow("camera", frame)
```

### Dlib Functions

#### `dlib.get_frontal_face_detector()`
**Used in**: `main.py`, `attendance_taker.py`, `features_extraction_to_csv.py`  
**Purpose**: Creates face detector object.  
**Usage**:
```python
detector = dlib.get_frontal_face_detector()
```

#### `dlib.shape_predictor()`
**Used in**: `attendance_taker.py`, `features_extraction_to_csv.py`  
**Purpose**: Creates facial landmark predictor.  
**Usage**:
```python
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
```

#### `dlib.face_recognition_model_v1()`
**Used in**: `attendance_taker.py`, `features_extraction_to_csv.py`  
**Purpose**: Creates face recognition model.  
**Usage**:
```python
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")
```

---

## Function Categories Summary

### Core Functions
- **Registration**: `Face_Register` class methods
- **Recognition**: `Face_Recognizer` class methods  
- **Feature Extraction**: Standalone functions in `features_extraction_to_csv.py`
- **Web Interface**: Flask routes in `app.py`

### Helper Functions
- **Database**: SQLite operations
- **Logging**: Python logging module
- **Video**: OpenCV functions
- **AI/ML**: Dlib functions

### Integration Points
- **Data Flow**: Registration → Feature Extraction → Recognition → Attendance Logging
- **File Dependencies**: Dlib models, CSV files, SQLite database
- **External Dependencies**: OpenCV, Dlib, Flask, Tkinter