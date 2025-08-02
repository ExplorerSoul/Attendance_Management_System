# Facial Recognition Attendance System - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Web Application API](#web-application-api)
4. [Face Registration System](#face-registration-system)
5. [Face Recognition System](#face-recognition-system)
6. [Feature Extraction System](#feature-extraction-system)
7. [Database Schema](#database-schema)
8. [Usage Examples](#usage-examples)
9. [Error Handling](#error-handling)
10. [Configuration](#configuration)

## Overview

The Facial Recognition Attendance System is a comprehensive Python application that provides face registration, real-time recognition, and attendance tracking capabilities. The system consists of multiple components working together to create a complete attendance management solution.

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Face Register │    │ Face Recognition │    │ Web Application │
│   (main.py)     │    │ (attendance_taker│    │ (app.py)        │
│                 │    │ .py)             │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Feature Extract │    │ SQLite Database  │    │ HTML Templates  │
│ (features_ext..)│    │ (attendance.db)  │    │ (templates/)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Classes

### 1. Face_Register Class (`main.py`)

**Purpose**: Handles face registration and image capture for new users.

**Location**: `main.py`

#### Constructor
```python
def __init__(self):
```
**Description**: Initializes the face registration system with GUI components and camera setup.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register = Face_Register()
```

#### Public Methods

##### `run()`
**Description**: Starts the face registration application.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register = Face_Register()
face_register.run()
```

##### `GUI_clear_data()`
**Description**: Clears all existing face data and resets the system.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register.GUI_clear_data()
```

##### `GUI_get_input_name()`
**Description**: Processes user input name and creates face folder.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register.GUI_get_input_name()
```

##### `save_current_face()`
**Description**: Saves the currently detected face as an image.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register.save_current_face()
```

##### `halt_program()`
**Description**: Safely halts the program and runs feature extraction.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_register.halt_program()
```

### 2. Face_Recognizer Class (`attendance_taker.py`)

**Purpose**: Handles real-time face recognition and attendance logging.

**Location**: `attendance_taker.py`

#### Constructor
```python
def __init__(self):
```
**Description**: Initializes the face recognition system with detection models and tracking variables.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_recognizer = Face_Recognizer()
```

#### Public Methods

##### `run()`
**Description**: Starts the face recognition and attendance system.

**Parameters**: None

**Returns**: None

**Example**:
```python
face_recognizer = Face_Recognizer()
face_recognizer.run()
```

##### `get_face_database()`
**Description**: Loads known faces from the features CSV file.

**Parameters**: None

**Returns**: 
- `1` if database loaded successfully
- `0` if database file not found

**Example**:
```python
success = face_recognizer.get_face_database()
if success:
    print("Database loaded successfully")
```

##### `attendance(name)`
**Description**: Records attendance for a recognized person.

**Parameters**:
- `name` (str): Name of the person to mark as present

**Returns**: None

**Example**:
```python
face_recognizer.attendance("John Doe")
```

##### `process(stream)`
**Description**: Main processing loop for face detection and recognition.

**Parameters**:
- `stream` (cv2.VideoCapture): Video stream object

**Returns**: None

**Example**:
```python
cap = cv2.VideoCapture(0)
face_recognizer.process(cap)
```

#### Static Methods

##### `return_euclidean_distance(feature_1, feature_2)`
**Description**: Calculates Euclidean distance between two 128D feature vectors.

**Parameters**:
- `feature_1` (numpy.ndarray): First feature vector
- `feature_2` (numpy.ndarray): Second feature vector

**Returns**: `float`: Euclidean distance between the features

**Example**:
```python
distance = Face_Recognizer.return_euclidean_distance(feature1, feature2)
```

## Web Application API (`app.py`)

### Flask Application Routes

#### `index()` Route
**URL**: `/`
**Method**: GET
**Description**: Displays the main attendance viewing interface.

**Parameters**: None

**Returns**: Rendered HTML template

**Example**:
```python
@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False)
```

#### `attendance()` Route
**URL**: `/attendance`
**Method**: POST
**Description**: Retrieves and displays attendance data for a selected date.

**Parameters**:
- `selected_date` (str): Date in YYYY-MM-DD format

**Returns**: Rendered HTML template with attendance data

**Example**:
```python
@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    # Process attendance data
    return render_template('index.html', selected_date=selected_date, attendance_data=data)
```

## Feature Extraction System (`features_extraction_to_csv.py`)

### Public Functions

#### `return_128d_features(path_img)`
**Description**: Extracts 128-dimensional feature vector from a single image.

**Parameters**:
- `path_img` (str): Path to the image file

**Returns**: 
- `numpy.ndarray`: 128D feature vector if face detected
- `0`: If no face detected

**Example**:
```python
features = return_128d_features("path/to/image.jpg")
if features != 0:
    print("Features extracted successfully")
```

#### `return_features_mean_personX(path_face_personX)`
**Description**: Calculates mean feature vector for all images of a person.

**Parameters**:
- `path_face_personX` (str): Path to directory containing person's images

**Returns**: `numpy.ndarray`: Mean 128D feature vector

**Example**:
```python
mean_features = return_features_mean_personX("data/data_faces_from_camera/person_1_john")
```

#### `main()`
**Description**: Main function that processes all registered faces and creates features CSV.

**Parameters**: None

**Returns**: None

**Example**:
```python
if __name__ == '__main__':
    main()
```

## Database Schema

### Attendance Table
**Table Name**: `attendance`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `name` | TEXT | NOT NULL | Person's name |
| `time` | TEXT | NOT NULL | Attendance time (HH:MM:SS) |
| `date` | DATE | NOT NULL | Attendance date (YYYY-MM-DD) |
| - | - | UNIQUE(name, date) | Prevents duplicate entries per person per day |

**SQL Creation**:
```sql
CREATE TABLE IF NOT EXISTS attendance (
    name TEXT, 
    time TEXT, 
    date DATE, 
    UNIQUE(name, date)
);
```

## Usage Examples

### 1. Complete Face Registration Workflow

```python
# Step 1: Register new faces
from main import Face_Register

# Initialize and run face registration
face_register = Face_Register()
face_register.run()

# Step 2: Extract features (automatically called when halting)
# This creates data/features_all.csv

# Step 3: Start attendance system
from attendance_taker import Face_Recognizer

face_recognizer = Face_Recognizer()
face_recognizer.run()
```

### 2. Web Application Usage

```python
# Start the web application
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 3. Manual Feature Extraction

```python
# Extract features from registered faces
from features_extraction_to_csv import main

main()
```

### 4. Database Operations

```python
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Insert attendance record
current_date = datetime.now().strftime('%Y-%m-%d')
current_time = datetime.now().strftime('%H:%M:%S')
cursor.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)", 
               ("John Doe", current_time, current_date))
conn.commit()

# Query attendance records
cursor.execute("SELECT * FROM attendance WHERE date = ?", (current_date,))
records = cursor.fetchall()

conn.close()
```

## Error Handling

### Common Error Scenarios

1. **No Camera Available**
   ```python
   # Error: No video input!!!
   # Solution: Check camera connection and permissions
   ```

2. **Missing Dlib Models**
   ```python
   # Error: 'data/data_dlib/shape_predictor_68_face_landmarks.dat' not found
   # Solution: Download required Dlib model files
   ```

3. **No Face Database**
   ```python
   # Warning: 'features_all.csv' not found!
   # Solution: Run face registration and feature extraction first
   ```

4. **Database Connection Issues**
   ```python
   # Error: Unable to open database file
   # Solution: Check file permissions and disk space
   ```

### Error Recovery

```python
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Handle camera errors
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Camera not available")
except Exception as e:
    print(f"Camera error: {e}")
    # Implement fallback or exit gracefully
```

## Configuration

### Required Files Structure
```
project_root/
├── data/
│   ├── data_dlib/
│   │   ├── shape_predictor_68_face_landmarks.dat
│   │   └── dlib_face_recognition_resnet_model_v1.dat
│   └── data_faces_from_camera/
├── templates/
│   └── index.html
├── resources/
├── main.py
├── attendance_taker.py
├── app.py
├── features_extraction_to_csv.py
└── attendance.db
```

### Environment Variables
```bash
# Optional: Set Flask environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Optional: Set camera device
export CAMERA_DEVICE=0
```

### Dependencies
```txt
dlib>=19.24.0
opencv-python>=4.5.0
numpy>=1.21.0
pandas>=1.3.0
flask>=2.0.0
pillow>=8.0.0
```

## Performance Considerations

### Memory Usage
- Face features are loaded into memory during recognition
- Large databases may require significant RAM
- Consider implementing pagination for large datasets

### Processing Speed
- Face detection: ~30 FPS on modern hardware
- Recognition accuracy improves with multiple face samples
- GPU acceleration available for dlib operations

### Storage Requirements
- Each face image: ~50-200 KB
- Features CSV: ~1 KB per person
- Database: ~100 bytes per attendance record

## Security Considerations

1. **Data Privacy**: Face images contain sensitive biometric data
2. **Access Control**: Implement authentication for web interface
3. **Data Encryption**: Consider encrypting stored face features
4. **Audit Logging**: Log all attendance operations
5. **Backup Strategy**: Regular backups of attendance database

## Troubleshooting

### Common Issues and Solutions

1. **Camera Not Working**
   - Check camera permissions
   - Verify camera is not in use by another application
   - Try different camera index (0, 1, 2, etc.)

2. **Face Detection Issues**
   - Ensure good lighting conditions
   - Position face clearly in camera view
   - Check if face is within detection range

3. **Recognition Accuracy**
   - Capture multiple face images during registration
   - Ensure face images are clear and well-lit
   - Adjust recognition threshold if needed

4. **Database Errors**
   - Check file permissions
   - Verify disk space
   - Ensure SQLite is properly installed

5. **Web Application Issues**
   - Check if port 5000 is available
   - Verify Flask installation
   - Check firewall settings

## API Versioning

Current Version: 1.0.0

### Version History
- v1.0.0: Initial release with basic face recognition and attendance tracking

### Backward Compatibility
- All APIs maintain backward compatibility within major versions
- Database schema changes will be documented in release notes

## Contributing

When contributing to this project:

1. Follow the existing code style
2. Add comprehensive documentation for new features
3. Include unit tests for new functionality
4. Update this documentation for API changes
5. Test on multiple platforms before submitting

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Last Updated**: December 2024  
**Documentation Version**: 1.0.0  
**Maintainer**: Development Team