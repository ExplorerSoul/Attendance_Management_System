# Function Reference - Facial Recognition Attendance System

## Table of Contents
1. [Face Registration Functions](#face-registration-functions)
2. [Face Recognition Functions](#face-recognition-functions)
3. [Feature Extraction Functions](#feature-extraction-functions)
4. [Web Application Functions](#web-application-functions)
5. [Utility Functions](#utility-functions)
6. [Database Functions](#database-functions)

---

## Face Registration Functions

### Class: Face_Register

#### `__init__(self)`
**File**: `main.py`  
**Purpose**: Initialize face registration system

**Parameters**: None  
**Returns**: None

**Description**: Sets up GUI components, camera, and initializes all tracking variables.

**Example**:
```python
face_register = Face_Register()
```

#### `run(self)`
**File**: `main.py`  
**Purpose**: Start the face registration application

**Parameters**: None  
**Returns**: None

**Description**: Initializes directories, sets up GUI, and starts the main processing loop.

**Example**:
```python
face_register = Face_Register()
face_register.run()
```

#### `GUI_clear_data(self)`
**File**: `main.py`  
**Purpose**: Clear all existing face data

**Parameters**: None  
**Returns**: None

**Description**: Removes all face folders and the features CSV file, resets counters.

**Example**:
```python
face_register.GUI_clear_data()
```

#### `GUI_get_input_name(self)`
**File**: `main.py`  
**Purpose**: Process user input name and create face folder

**Parameters**: None  
**Returns**: None

**Description**: Gets name from GUI input field and creates directory for face storage.

**Example**:
```python
face_register.GUI_get_input_name()
```

#### `save_current_face(self)`
**File**: `main.py`  
**Purpose**: Save the currently detected face as an image

**Parameters**: None  
**Returns**: None

**Description**: Captures the face ROI and saves it as a JPEG image in the person's folder.

**Example**:
```python
face_register.save_current_face()
```

#### `halt_program(self)`
**File**: `main.py`  
**Purpose**: Safely halt the program and run feature extraction

**Parameters**: None  
**Returns**: None

**Description**: Releases camera, runs feature extraction script, and closes GUI.

**Example**:
```python
face_register.halt_program()
```

#### `pre_work_mkdir(self)`
**File**: `main.py`  
**Purpose**: Create necessary directories

**Parameters**: None  
**Returns**: None

**Description**: Creates the main photos directory if it doesn't exist.

**Example**:
```python
face_register.pre_work_mkdir()
```

#### `check_existing_faces_cnt(self)`
**File**: `main.py`  
**Purpose**: Count existing registered faces

**Parameters**: None  
**Returns**: None

**Description**: Scans existing face folders to determine the next person number.

**Example**:
```python
face_register.check_existing_faces_cnt()
```

#### `update_fps(self)`
**File**: `main.py`  
**Purpose**: Update FPS calculation

**Parameters**: None  
**Returns**: None

**Description**: Calculates and updates the frames per second display.

**Example**:
```python
face_register.update_fps()
```

#### `create_face_folder(self)`
**File**: `main.py`  
**Purpose**: Create folder for new person

**Parameters**: None  
**Returns**: None

**Description**: Creates a new directory for storing face images of a new person.

**Example**:
```python
face_register.create_face_folder()
```

#### `get_frame(self)`
**File**: `main.py`  
**Purpose**: Capture frame from camera

**Parameters**: None  
**Returns**: Tuple (bool, numpy.ndarray)

**Description**: Captures a frame from the camera and converts it to RGB format.

**Example**:
```python
ret, frame = face_register.get_frame()
if ret:
    # Process frame
```

#### `process(self)`
**File**: `main.py`  
**Purpose**: Main processing loop for face detection

**Parameters**: None  
**Returns**: None

**Description**: Continuously processes video frames, detects faces, and updates GUI.

**Example**:
```python
face_register.process()
```

---

## Face Recognition Functions

### Class: Face_Recognizer

#### `__init__(self)`
**File**: `attendance_taker.py`  
**Purpose**: Initialize face recognition system

**Parameters**: None  
**Returns**: None

**Description**: Sets up face detection models, tracking variables, and recognition parameters.

**Example**:
```python
recognizer = Face_Recognizer()
```

#### `run(self)`
**File**: `attendance_taker.py`  
**Purpose**: Start the face recognition system

**Parameters**: None  
**Returns**: None

**Description**: Initializes camera and starts the main recognition loop.

**Example**:
```python
recognizer = Face_Recognizer()
recognizer.run()
```

#### `get_face_database(self)`
**File**: `attendance_taker.py`  
**Purpose**: Load known faces from CSV file

**Parameters**: None  
**Returns**: int (1 for success, 0 for failure)

**Description**: Reads the features CSV file and loads known face features and names.

**Example**:
```python
success = recognizer.get_face_database()
if success:
    print("Database loaded successfully")
```

#### `attendance(self, name)`
**File**: `attendance_taker.py`  
**Purpose**: Record attendance for a person

**Parameters**:
- `name` (str): Name of the person to mark as present

**Returns**: None

**Description**: Inserts attendance record into database with current date and time.

**Example**:
```python
recognizer.attendance("John Doe")
```

#### `update_fps(self)`
**File**: `attendance_taker.py`  
**Purpose**: Update FPS calculation

**Parameters**: None  
**Returns**: None

**Description**: Calculates and updates the frames per second.

**Example**:
```python
recognizer.update_fps()
```

#### `return_euclidean_distance(feature_1, feature_2)`
**File**: `attendance_taker.py`  
**Purpose**: Calculate Euclidean distance between feature vectors

**Parameters**:
- `feature_1` (numpy.ndarray): First 128D feature vector
- `feature_2` (numpy.ndarray): Second 128D feature vector

**Returns**: float

**Description**: Calculates the Euclidean distance between two 128-dimensional feature vectors.

**Example**:
```python
distance = Face_Recognizer.return_euclidean_distance(feature1, feature2)
```

#### `centroid_tracker(self)`
**File**: `attendance_taker.py`  
**Purpose**: Track faces between frames using centroid

**Parameters**: None  
**Returns**: None

**Description**: Links faces in current frame with faces in previous frame using centroid positions.

**Example**:
```python
recognizer.centroid_tracker()
```

#### `draw_note(self, img_rd)`
**File**: `attendance_taker.py`  
**Purpose**: Draw information on video frame

**Parameters**:
- `img_rd` (numpy.ndarray): Image to draw on

**Returns**: numpy.ndarray

**Description**: Adds text information (FPS, frame count, face count) to the video frame.

**Example**:
```python
img_with_text = recognizer.draw_note(frame)
```

#### `process(self, stream)`
**File**: `attendance_taker.py`  
**Purpose**: Main processing loop for face recognition

**Parameters**:
- `stream` (cv2.VideoCapture): Video stream object

**Returns**: None

**Description**: Main loop that processes video frames, detects faces, recognizes them, and records attendance.

**Example**:
```python
cap = cv2.VideoCapture(0)
recognizer.process(cap)
```

---

## Feature Extraction Functions

### `return_128d_features(path_img)`
**File**: `features_extraction_to_csv.py`  
**Purpose**: Extract 128D features from a single image

**Parameters**:
- `path_img` (str): Path to the image file

**Returns**: numpy.ndarray or int (0 if no face detected)

**Description**: Detects face in image and extracts 128-dimensional feature vector using dlib.

**Example**:
```python
features = return_128d_features("data/data_faces_from_camera/person_1/img_face_1.jpg")
if features != 0:
    print("Features extracted successfully")
```

### `return_features_mean_personX(path_face_personX)`
**File**: `features_extraction_to_csv.py`  
**Purpose**: Calculate mean features for all images of a person

**Parameters**:
- `path_face_personX` (str): Path to directory containing person's images

**Returns**: numpy.ndarray

**Description**: Processes all images in a person's folder and calculates the mean feature vector.

**Example**:
```python
mean_features = return_features_mean_personX("data/data_faces_from_camera/person_1_john")
```

### `main()`
**File**: `features_extraction_to_csv.py`  
**Purpose**: Main function for feature extraction

**Parameters**: None  
**Returns**: None

**Description**: Processes all registered faces and creates the features CSV file.

**Example**:
```python
from features_extraction_to_csv import main
main()
```

---

## Web Application Functions

### `index()`
**File**: `app.py`  
**Purpose**: Display main attendance viewing interface

**Parameters**: None  
**Returns**: Flask response

**Description**: Renders the main HTML template with attendance form.

**Example**:
```python
@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False)
```

### `attendance()`
**File**: `app.py`  
**Purpose**: Handle attendance data retrieval

**Parameters**: None (gets data from request.form)  
**Returns**: Flask response

**Description**: Processes date selection and retrieves attendance data from database.

**Example**:
```python
@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    # Process and return attendance data
```

---

## Utility Functions

### `main()` (main.py)
**File**: `main.py`  
**Purpose**: Entry point for face registration

**Parameters**: None  
**Returns**: None

**Description**: Sets up logging and starts the face registration application.

**Example**:
```python
if __name__ == '__main__':
    main()
```

### `main()` (attendance_taker.py)
**File**: `attendance_taker.py`  
**Purpose**: Entry point for face recognition

**Parameters**: None  
**Returns**: None

**Description**: Sets up logging and starts the face recognition application.

**Example**:
```python
if __name__ == '__main__':
    main()
```

### `main()` (features_extraction_to_csv.py)
**File**: `features_extraction_to_csv.py`  
**Purpose**: Entry point for feature extraction

**Parameters**: None  
**Returns**: None

**Description**: Sets up logging and runs the feature extraction process.

**Example**:
```python
if __name__ == '__main__':
    main()
```

---

## Database Functions

### Database Connection
**File**: `attendance_taker.py`  
**Purpose**: Create database connection and table

**Code**:
```python
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()
create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (name TEXT, time TEXT, date DATE, UNIQUE(name, date))"
cursor.execute(create_table_sql)
conn.commit()
conn.close()
```

### Attendance Insertion
**File**: `attendance_taker.py`  
**Function**: `attendance(self, name)`

**SQL**:
```sql
INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)
```

### Attendance Retrieval
**File**: `app.py`  
**Function**: `attendance()`

**SQL**:
```sql
SELECT name, time FROM attendance WHERE date = ?
```

---

## Function Categories Summary

### Face Registration (main.py)
- **Initialization**: `__init__()`, `pre_work_mkdir()`, `check_existing_faces_cnt()`
- **GUI Operations**: `GUI_clear_data()`, `GUI_get_input_name()`, `GUI_info()`
- **Face Processing**: `save_current_face()`, `create_face_folder()`
- **Video Processing**: `get_frame()`, `process()`, `update_fps()`
- **Program Control**: `run()`, `halt_program()`

### Face Recognition (attendance_taker.py)
- **Initialization**: `__init__()`, `get_face_database()`
- **Recognition**: `process()`, `centroid_tracker()`
- **Attendance**: `attendance()`
- **Utilities**: `update_fps()`, `draw_note()`, `return_euclidean_distance()`
- **Program Control**: `run()`

### Feature Extraction (features_extraction_to_csv.py)
- **Feature Extraction**: `return_128d_features()`, `return_features_mean_personX()`
- **Main Process**: `main()`

### Web Application (app.py)
- **Routes**: `index()`, `attendance()`
- **Program Control**: `app.run()`

### Database Operations
- **Connection**: SQLite connection setup
- **Insertion**: Attendance record insertion
- **Retrieval**: Attendance data querying

---

## Function Dependencies

### Core Dependencies
```
Face_Register.__init__()
├── cv2.VideoCapture()
├── tkinter.Tk()
└── dlib.get_frontal_face_detector()

Face_Recognizer.__init__()
├── dlib.get_frontal_face_detector()
├── dlib.shape_predictor()
└── dlib.face_recognition_model_v1()

return_128d_features()
├── cv2.imread()
├── detector()
├── predictor()
└── face_reco_model.compute_face_descriptor()
```

### Data Flow Dependencies
```
Face_Register.run()
├── pre_work_mkdir()
├── check_existing_faces_cnt()
├── GUI_info()
└── process()

Face_Recognizer.run()
├── get_face_database()
└── process()

process() (Face_Recognizer)
├── detector()
├── predictor()
├── face_reco_model.compute_face_descriptor()
├── return_euclidean_distance()
├── centroid_tracker()
├── attendance()
└── draw_note()
```

---

## Error Handling in Functions

### Common Error Patterns

1. **Camera Errors**
   ```python
   try:
       ret, frame = self.get_frame()
   except:
       print("Error: No video input!!!")
   ```

2. **File Not Found**
   ```python
   if os.path.exists("data/features_all.csv"):
       # Process file
   else:
       logging.warning("'features_all.csv' not found!")
   ```

3. **Database Errors**
   ```python
   try:
       conn = sqlite3.connect("attendance.db")
       # Database operations
   except Exception as e:
       print(f"Database error: {e}")
   ```

4. **Face Detection Errors**
   ```python
   if len(faces) != 0:
       # Process face
   else:
       logging.warning("no face")
   ```

---

## Performance Considerations

### Memory-Intensive Functions
- `get_face_database()`: Loads all face features into memory
- `process()`: Continuously processes video frames
- `return_features_mean_personX()`: Processes multiple images

### CPU-Intensive Functions
- `return_128d_features()`: Face detection and feature extraction
- `return_euclidean_distance()`: Mathematical calculations
- `centroid_tracker()`: Distance calculations for tracking

### I/O-Intensive Functions
- `save_current_face()`: Image file writing
- `attendance()`: Database operations
- `main()` (features_extraction_to_csv.py): CSV file writing

---

**Function Reference Version**: 1.0.0  
**Last Updated**: December 2024