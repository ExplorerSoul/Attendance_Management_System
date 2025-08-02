# Quick Reference Guide - Facial Recognition Attendance System

## 🚀 Quick Start

### 1. Face Registration
```python
from main import Face_Register

# Start face registration GUI
face_register = Face_Register()
face_register.run()
```

### 2. Face Recognition & Attendance
```python
from attendance_taker import Face_Recognizer

# Start attendance system
recognizer = Face_Recognizer()
recognizer.run()
```

### 3. Web Application
```python
from app import app

# Start web server
app.run(debug=True, port=5000)
```

## 📋 API Quick Reference

### Core Classes

| Class | File | Purpose | Main Method |
|-------|------|---------|-------------|
| `Face_Register` | `main.py` | Face registration | `run()` |
| `Face_Recognizer` | `attendance_taker.py` | Face recognition | `run()` |
| Flask App | `app.py` | Web interface | `app.run()` |

### Key Methods

#### Face_Register Methods
```python
face_register = Face_Register()

# Clear all data
face_register.GUI_clear_data()

# Save current face
face_register.save_current_face()

# Halt program (auto-runs feature extraction)
face_register.halt_program()
```

#### Face_Recognizer Methods
```python
recognizer = Face_Recognizer()

# Load face database
success = recognizer.get_face_database()

# Manual attendance recording
recognizer.attendance("John Doe")

# Process video stream
cap = cv2.VideoCapture(0)
recognizer.process(cap)
```

#### Feature Extraction
```python
from features_extraction_to_csv import return_128d_features, return_features_mean_personX

# Extract features from single image
features = return_128d_features("path/to/image.jpg")

# Get mean features for person
mean_features = return_features_mean_personX("data/data_faces_from_camera/person_1")
```

### Web API Endpoints

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/` | GET | Show attendance form | None |
| `/attendance` | POST | Get attendance data | `selected_date` |

### Database Operations

```python
import sqlite3
from datetime import datetime

# Connect
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Insert attendance
cursor.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)", 
               ("John", "09:30:00", "2024-12-01"))

# Query attendance
cursor.execute("SELECT * FROM attendance WHERE date = ?", ("2024-12-01",))
records = cursor.fetchall()

conn.commit()
conn.close()
```

## 🔧 Configuration

### Required Files
```
data/data_dlib/
├── shape_predictor_68_face_landmarks.dat
└── dlib_face_recognition_resnet_model_v1.dat
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set Flask environment (optional)
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## 📊 Data Flow

```
1. Face Registration (main.py)
   ↓
2. Feature Extraction (features_extraction_to_csv.py)
   ↓
3. Face Recognition (attendance_taker.py)
   ↓
4. Database Storage (SQLite)
   ↓
5. Web Viewing (app.py)
```

## 🐛 Common Issues

### Camera Issues
```python
# Try different camera index
cap = cv2.VideoCapture(1)  # or 2, 3, etc.

# Check if camera is working
if not cap.isOpened():
    print("Camera not available")
```

### Missing Files
```python
# Check if required files exist
import os
required_files = [
    "data/data_dlib/shape_predictor_68_face_landmarks.dat",
    "data/data_dlib/dlib_face_recognition_resnet_model_v1.dat"
]

for file in required_files:
    if not os.path.exists(file):
        print(f"Missing: {file}")
```

### Database Issues
```python
# Check database connection
try:
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
except Exception as e:
    print(f"Database error: {e}")
```

## 📈 Performance Tips

### Recognition Accuracy
- Capture 5-10 face images per person
- Ensure good lighting during registration
- Position face clearly in camera view

### Processing Speed
- Use GPU if available for dlib operations
- Reduce video resolution if needed
- Close unnecessary applications

### Memory Usage
- Large face databases may require more RAM
- Consider implementing pagination for web interface
- Regular cleanup of old face images

## 🔒 Security Notes

```python
# Basic authentication example
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

def authenticate():
    return Response('Could not verify your access level for that URL.\n'
                   'You have to login with proper credentials', 401,
                   {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Apply to routes
@app.route('/')
@requires_auth
def index():
    return render_template('index.html')
```

## 📝 Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance.log'),
        logging.StreamHandler()
    ]
)

# Use in code
logging.info("Face recognized: John Doe")
logging.warning("No face detected in frame")
logging.error("Database connection failed")
```

## 🧪 Testing

### Basic Test Example
```python
import unittest
from main import Face_Register
from attendance_taker import Face_Recognizer

class TestAttendanceSystem(unittest.TestCase):
    
    def test_face_register_initialization(self):
        register = Face_Register()
        self.assertIsNotNone(register)
    
    def test_recognizer_initialization(self):
        recognizer = Face_Recognizer()
        self.assertIsNotNone(recognizer)
    
    def test_euclidean_distance(self):
        import numpy as np
        feature1 = np.random.rand(128)
        feature2 = np.random.rand(128)
        distance = Face_Recognizer.return_euclidean_distance(feature1, feature2)
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)

if __name__ == '__main__':
    unittest.main()
```

## 📞 Support

### Debug Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Flask debug mode
app.run(debug=True)
```

### Common Commands
```bash
# Run face registration
python main.py

# Run attendance system
python attendance_taker.py

# Run web application
python app.py

# Extract features manually
python features_extraction_to_csv.py
```

---

**Quick Reference Version**: 1.0.0  
**Last Updated**: December 2024