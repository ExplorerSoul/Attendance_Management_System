# Quick Reference Guide - Facial Recognition Attendance System

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download Dlib models (required)
# Visit: https://drive.google.com/drive/folders/1MJ86CfAg3ZfjAhHwn8-BoqdpIqsxah25?usp=sharing
# Place files in data/data_dlib/
```

### 2. Register Faces
```bash
python main.py
# Follow GUI: Clear → Enter Name → Input → Save Faces → HLT
```

### 3. Take Attendance
```bash
python attendance_taker.py
# Press 'q' to quit
```

### 4. View Records
```bash
python app.py
# Open http://localhost:5000
```

## 📋 API Quick Reference

### Core Classes

#### Face_Register (`main.py`)
```python
# Initialize
register = Face_Register()

# Main methods
register.run()                    # Start registration GUI
register.GUI_clear_data()         # Clear all face data
register.save_current_face()      # Save detected face
register.halt_program()           # Stop and extract features
```

#### Face_Recognizer (`attendance_taker.py`)
```python
# Initialize
recognizer = Face_Recognizer()

# Main methods
recognizer.run()                  # Start recognition system
recognizer.get_face_database()    # Load known faces (returns 1/0)
recognizer.attendance(name)       # Log attendance for person
recognizer.process(stream)        # Main recognition loop

# Static methods
Face_Recognizer.return_euclidean_distance(f1, f2)  # Calculate distance
```

### Web API (`app.py`)
```python
# Routes
GET  /                    # Main page
POST /attendance          # Get attendance data for date
```

### Feature Extraction (`features_extraction_to_csv.py`)
```python
# Functions
return_128d_features(path_img)           # Extract features from image
return_features_mean_personX(path_dir)   # Get mean features for person
main()                                   # Process all faces to CSV
```

## 🗄️ Database Schema

```sql
-- attendance.db
CREATE TABLE attendance (
    name TEXT,
    time TEXT,      -- HH:MM:SS format
    date DATE,      -- YYYY-MM-DD format
    UNIQUE(name, date)
);
```

## 📁 File Structure

```
project/
├── main.py                          # Face registration
├── attendance_taker.py              # Face recognition  
├── features_extraction_to_csv.py    # Feature extraction
├── app.py                          # Web interface
├── attendance.db                   # SQLite database
├── data/
│   ├── data_faces_from_camera/     # Face images
│   ├── data_dlib/                  # Dlib models
│   └── features_all.csv           # Face features
└── templates/index.html            # Web template
```

## ⚙️ Configuration

### Key Parameters
```python
# Face recognition threshold
RECOGNITION_THRESHOLD = 0.4

# Reclassification interval
RECLASSIFY_INTERVAL = 10

# Video resolution
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
```

### Logging Levels
```python
# Debug (detailed info)
logging.basicConfig(level=logging.DEBUG)

# Info (standard)
logging.basicConfig(level=logging.INFO)
```

## 🔧 Common Operations

### Register New Person
```python
# 1. Start registration
python main.py

# 2. GUI steps:
#    - Click "Clear"
#    - Enter name
#    - Click "Input" 
#    - Click "Save current face" (multiple times)
#    - Click "HLT"
```

### Take Attendance
```python
# Start recognition
python attendance_taker.py

# System will:
# - Load known faces
# - Start video capture
# - Recognize faces in real-time
# - Log attendance automatically
# - Press 'q' to quit
```

### View Attendance
```python
# Start web server
python app.py

# Open browser: http://localhost:5000
# Select date to view records
```

### Extract Features Manually
```python
# Process all registered faces
python features_extraction_to_csv.py

# Creates: data/features_all.csv
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Camera not found | Check camera connection and permissions |
| Dlib models missing | Download from Google Drive link |
| No faces detected | Improve lighting and positioning |
| Database locked | Close other applications using DB |
| Recognition poor | Add more face images per person |

### Error Messages
```python
"Error: No video input!!!"           # Camera issue
"shape_predictor_68_face_landmarks.dat not found"  # Missing Dlib models
"No face in current frame!"          # Face not visible
"database is locked"                 # DB access conflict
```

## 📊 Performance Tips

1. **Face Registration**: Capture 5-10 images per person
2. **Lighting**: Ensure good, consistent lighting
3. **Positioning**: Face should be clearly visible
4. **Distance**: Stay 1-2 meters from camera
5. **Background**: Use plain background for better detection

## 🔒 Security Notes

- Face data stored locally only
- No encryption on database
- Web interface has no authentication
- Camera access requires user permission

## 📝 Code Examples

### Custom Face Recognition
```python
from attendance_taker import Face_Recognizer

# Initialize
recognizer = Face_Recognizer()

# Load database
if recognizer.get_face_database():
    # Process video stream
    cap = cv2.VideoCapture(0)
    recognizer.process(cap)
    cap.release()
```

### Custom Attendance Logging
```python
from attendance_taker import Face_Recognizer

recognizer = Face_Recognizer()
recognizer.attendance("John Doe")  # Log attendance for John
```

### Feature Extraction
```python
from features_extraction_to_csv import return_128d_features

# Extract features from image
features = return_128d_features("path/to/face.jpg")
if features != 0:
    print("Features extracted:", len(features))
```

## 📞 Support

- **Documentation**: See `API_DOCUMENTATION.md`
- **Issues**: Check troubleshooting section
- **Models**: Download from provided Google Drive link
- **Dependencies**: See `requirements.txt`