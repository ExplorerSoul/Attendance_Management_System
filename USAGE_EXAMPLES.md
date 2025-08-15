# Usage Examples - Facial Recognition Attendance System

## Table of Contents
1. [Basic Setup Examples](#basic-setup-examples)
2. [Face Registration Examples](#face-registration-examples)
3. [Face Recognition Examples](#face-recognition-examples)
4. [Feature Extraction Examples](#feature-extraction-examples)
5. [Web Application Examples](#web-application-examples)
6. [Database Operations](#database-operations)
7. [Custom Integration Examples](#custom-integration-examples)
8. [Error Handling Examples](#error-handling-examples)
9. [Performance Optimization Examples](#performance-optimization-examples)

---

## Basic Setup Examples

### 1. Complete System Setup

```python
# 1. Install dependencies
import subprocess
import sys

def install_dependencies():
    """Install required packages"""
    packages = [
        'dlib',
        'opencv-python',
        'numpy',
        'pandas',
        'flask',
        'pillow'
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# 2. Create required directories
import os

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/data_faces_from_camera',
        'data/data_dlib',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# 3. Download Dlib models (manual step required)
def check_dlib_models():
    """Check if required Dlib models exist"""
    required_files = [
        'data/data_dlib/shape_predictor_68_face_landmarks.dat',
        'data/data_dlib/dlib_face_recognition_resnet_model_v1.dat'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing Dlib model files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("Please download from: https://drive.google.com/drive/folders/1MJ86CfAg3ZfjAhHwn8-BoqdpIqsxah25?usp=sharing")
        return False
    
    return True

# Setup complete system
if __name__ == '__main__':
    install_dependencies()
    create_directories()
    if check_dlib_models():
        print("System setup complete!")
    else:
        print("Setup incomplete - missing Dlib models")
```

### 2. Environment Validation

```python
import importlib
import cv2
import dlib
import numpy as np
import pandas as pd
import flask
from PIL import Image

def validate_environment():
    """Validate that all required packages are available"""
    required_modules = {
        'cv2': 'OpenCV',
        'dlib': 'Dlib',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'flask': 'Flask',
        'PIL': 'Pillow'
    }
    
    missing_modules = []
    for module_name, display_name in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {display_name} available")
        except ImportError:
            missing_modules.append(display_name)
            print(f"✗ {display_name} missing")
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        return False
    
    print("\nAll required modules are available!")
    return True

# Test camera access
def test_camera():
    """Test camera access"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ Camera not accessible")
        return False
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        print("✓ Camera accessible")
        return True
    else:
        print("✗ Camera not accessible")
        return False

if __name__ == '__main__':
    validate_environment()
    test_camera()
```

---

## Face Registration Examples

### 1. Basic Face Registration

```python
from main import Face_Register

def register_new_person():
    """Register a new person using the GUI"""
    register = Face_Register()
    register.run()

# Usage
if __name__ == '__main__':
    register_new_person()
```

### 2. Programmatic Face Registration

```python
import cv2
import os
import numpy as np
from main import Face_Register

class CustomFaceRegister:
    def __init__(self):
        self.register = Face_Register()
    
    def register_person_programmatically(self, name, num_images=10):
        """Register a person with specified number of images"""
        # Clear existing data
        self.register.GUI_clear_data()
        
        # Set name
        self.register.input_name.delete(0, 'end')
        self.register.input_name.insert(0, name)
        self.register.GUI_get_input_name()
        
        # Capture images
        images_captured = 0
        while images_captured < num_images:
            ret, frame = self.register.get_frame()
            if ret and self.register.current_frame_faces_cnt == 1:
                self.register.save_current_face()
                images_captured += 1
                print(f"Captured image {images_captured}/{num_images}")
        
        # Extract features
        self.register.halt_program()
        print(f"Registration complete for {name}")

# Usage
if __name__ == '__main__':
    custom_register = CustomFaceRegister()
    custom_register.register_person_programmatically("John Doe", 5)
```

### 3. Batch Registration

```python
import os
from main import Face_Register

def batch_register(people_list):
    """Register multiple people in sequence"""
    register = Face_Register()
    
    for person in people_list:
        print(f"Registering {person['name']}...")
        
        # Clear data for each person
        register.GUI_clear_data()
        
        # Set name
        register.input_name.delete(0, 'end')
        register.input_name.insert(0, person['name'])
        register.GUI_get_input_name()
        
        # Capture specified number of images
        for i in range(person.get('num_images', 5)):
            register.save_current_face()
        
        print(f"Completed registration for {person['name']}")
    
    # Extract features for all
    register.halt_program()

# Usage
people_to_register = [
    {'name': 'Alice Johnson', 'num_images': 8},
    {'name': 'Bob Smith', 'num_images': 6},
    {'name': 'Carol Davis', 'num_images': 7}
]

batch_register(people_to_register)
```

### 4. Face Quality Validation

```python
import cv2
import numpy as np
from main import Face_Register

class QualityFaceRegister(Face_Register):
    def __init__(self):
        super().__init__()
        self.quality_threshold = 0.7
    
    def assess_face_quality(self, face_image):
        """Assess the quality of a captured face image"""
        # Convert to grayscale
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
        
        # Calculate brightness
        brightness = np.mean(gray)
        
        # Calculate contrast
        contrast = np.std(gray)
        
        # Calculate sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Normalize scores
        brightness_score = min(brightness / 128, 1.0)
        contrast_score = min(contrast / 50, 1.0)
        sharpness_score = min(sharpness / 100, 1.0)
        
        # Overall quality score
        quality_score = (brightness_score + contrast_score + sharpness_score) / 3
        
        return quality_score
    
    def save_current_face_with_quality_check(self):
        """Save face only if quality is acceptable"""
        if self.face_folder_created_flag and self.current_frame_faces_cnt == 1:
            if not self.out_of_range_flag:
                # Assess quality
                quality = self.assess_face_quality(self.face_ROI_image)
                
                if quality >= self.quality_threshold:
                    self.save_current_face()
                    print(f"Face saved with quality score: {quality:.2f}")
                else:
                    print(f"Face rejected - quality score: {quality:.2f} (threshold: {self.quality_threshold})")
            else:
                print("Face out of range")

# Usage
if __name__ == '__main__':
    quality_register = QualityFaceRegister()
    quality_register.run()
```

---

## Face Recognition Examples

### 1. Basic Face Recognition

```python
from attendance_taker import Face_Recognizer

def basic_recognition():
    """Basic face recognition and attendance logging"""
    recognizer = Face_Recognizer()
    recognizer.run()

# Usage
if __name__ == '__main__':
    basic_recognition()
```

### 2. Custom Recognition with Callbacks

```python
import cv2
from attendance_taker import Face_Recognizer

class CustomRecognizer(Face_Recognizer):
    def __init__(self):
        super().__init__()
        self.attendance_callbacks = []
        self.recognition_callbacks = []
    
    def add_attendance_callback(self, callback):
        """Add callback for attendance events"""
        self.attendance_callbacks.append(callback)
    
    def add_recognition_callback(self, callback):
        """Add callback for recognition events"""
        self.recognition_callbacks.append(callback)
    
    def attendance(self, name):
        """Override attendance method to include callbacks"""
        super().attendance(name)
        
        # Execute callbacks
        for callback in self.attendance_callbacks:
            callback(name)
    
    def process(self, stream):
        """Override process method to include recognition callbacks"""
        if self.get_face_database():
            while stream.isOpened():
                # ... existing process logic ...
                
                # Execute recognition callbacks for recognized faces
                for i, name in enumerate(self.current_frame_face_name_list):
                    if name != "unknown":
                        for callback in self.recognition_callbacks:
                            callback(name, i)

# Usage with callbacks
def on_attendance(name):
    print(f"Attendance logged for: {name}")

def on_recognition(name, face_index):
    print(f"Face {face_index + 1} recognized as: {name}")

if __name__ == '__main__':
    custom_recognizer = CustomRecognizer()
    custom_recognizer.add_attendance_callback(on_attendance)
    custom_recognizer.add_recognition_callback(on_recognition)
    custom_recognizer.run()
```

### 3. Recognition with Confidence Scores

```python
from attendance_taker import Face_Recognizer
import numpy as np

class ConfidenceRecognizer(Face_Recognizer):
    def __init__(self, confidence_threshold=0.4):
        super().__init__()
        self.confidence_threshold = confidence_threshold
        self.confidence_scores = []
    
    def process(self, stream):
        """Override process to include confidence scores"""
        if self.get_face_database():
            while stream.isOpened():
                # ... existing detection logic ...
                
                # Calculate confidence scores
                for k in range(len(faces)):
                    self.current_frame_face_X_e_distance_list = []
                    
                    for i in range(len(self.face_features_known_list)):
                        if str(self.face_features_known_list[i][0]) != '0.0':
                            e_distance = self.return_euclidean_distance(
                                self.current_frame_face_feature_list[k],
                                self.face_features_known_list[i]
                            )
                            self.current_frame_face_X_e_distance_list.append(e_distance)
                    
                    # Find best match with confidence
                    min_distance = min(self.current_frame_face_X_e_distance_list)
                    confidence = 1.0 - min(min_distance / 1.0, 1.0)  # Normalize to 0-1
                    
                    if min_distance < self.confidence_threshold:
                        similar_person_num = self.current_frame_face_X_e_distance_list.index(min_distance)
                        name = self.face_name_known_list[similar_person_num]
                        self.current_frame_face_name_list[k] = name
                        print(f"Recognized {name} with confidence: {confidence:.2f}")
                        
                        if confidence > 0.8:  # High confidence threshold for attendance
                            self.attendance(name)
                    else:
                        print(f"Unknown person (confidence: {confidence:.2f})")

# Usage
if __name__ == '__main__':
    confidence_recognizer = ConfidenceRecognizer(confidence_threshold=0.3)
    confidence_recognizer.run()
```

### 4. Multi-Face Tracking

```python
from attendance_taker import Face_Recognizer
import cv2

class MultiFaceTracker(Face_Recognizer):
    def __init__(self):
        super().__init__()
        self.face_tracks = {}  # Track faces across frames
        self.track_id = 0
    
    def update_tracks(self, faces, face_names):
        """Update face tracking information"""
        current_tracks = {}
        
        for i, (face, name) in enumerate(zip(faces, face_names)):
            # Calculate centroid
            centroid = (int((face.left() + face.right()) / 2),
                       int((face.top() + face.bottom()) / 2))
            
            # Find closest existing track
            min_distance = float('inf')
            best_track_id = None
            
            for track_id, track_info in self.face_tracks.items():
                distance = np.sqrt((centroid[0] - track_info['centroid'][0])**2 + 
                                 (centroid[1] - track_info['centroid'][1])**2)
                if distance < min_distance and distance < 100:  # 100 pixel threshold
                    min_distance = distance
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                current_tracks[best_track_id] = {
                    'centroid': centroid,
                    'name': name,
                    'frames_seen': self.face_tracks[best_track_id]['frames_seen'] + 1
                }
            else:
                # Create new track
                self.track_id += 1
                current_tracks[self.track_id] = {
                    'centroid': centroid,
                    'name': name,
                    'frames_seen': 1
                }
        
        self.face_tracks = current_tracks
        
        # Log attendance for faces seen for multiple frames
        for track_id, track_info in self.face_tracks.items():
            if track_info['frames_seen'] >= 5 and track_info['name'] != "unknown":
                self.attendance(track_info['name'])

# Usage
if __name__ == '__main__':
    tracker = MultiFaceTracker()
    tracker.run()
```

---

## Feature Extraction Examples

### 1. Basic Feature Extraction

```python
from features_extraction_to_csv import return_128d_features, return_features_mean_personX

def extract_single_face_features(image_path):
    """Extract features from a single face image"""
    features = return_128d_features(image_path)
    
    if features != 0:
        print(f"Features extracted: {len(features)} dimensions")
        print(f"Feature vector: {features[:5]}...")  # Show first 5 values
        return features
    else:
        print("No face detected in image")
        return None

def extract_person_features(person_folder):
    """Extract mean features for a person"""
    mean_features = return_features_mean_personX(person_folder)
    print(f"Mean features for person: {len(mean_features)} dimensions")
    return mean_features

# Usage
if __name__ == '__main__':
    # Extract from single image
    features = extract_single_face_features("data/data_faces_from_camera/person_1_john/img_face_1.jpg")
    
    # Extract mean features for person
    mean_features = extract_person_features("data/data_faces_from_camera/person_1_john")
```

### 2. Batch Feature Extraction

```python
import os
import pandas as pd
from features_extraction_to_csv import return_features_mean_personX

def batch_extract_features():
    """Extract features for all registered persons"""
    base_path = "data/data_faces_from_camera"
    features_data = []
    
    if not os.path.exists(base_path):
        print("No registered faces found")
        return
    
    person_folders = os.listdir(base_path)
    person_folders.sort()
    
    for person_folder in person_folders:
        person_path = os.path.join(base_path, person_folder)
        
        if os.path.isdir(person_path):
            print(f"Processing {person_folder}...")
            
            # Extract mean features
            mean_features = return_features_mean_personX(person_path)
            
            # Get person name
            if len(person_folder.split('_', 2)) == 2:
                person_name = person_folder
            else:
                person_name = person_folder.split('_', 2)[-1]
            
            # Create feature row
            feature_row = [person_name] + list(mean_features)
            features_data.append(feature_row)
            
            print(f"Completed {person_name}")
    
    # Save to CSV
    if features_data:
        df = pd.DataFrame(features_data)
        df.to_csv("data/features_all.csv", index=False, header=False)
        print(f"Features saved for {len(features_data)} persons")
    else:
        print("No features extracted")

# Usage
if __name__ == '__main__':
    batch_extract_features()
```

### 3. Feature Quality Assessment

```python
import numpy as np
from features_extraction_to_csv import return_128d_features
import os

class FeatureQualityAssessor:
    def __init__(self):
        self.quality_metrics = {}
    
    def assess_feature_quality(self, features):
        """Assess the quality of extracted features"""
        if features is None or len(features) == 0:
            return 0.0
        
        # Calculate feature statistics
        features_array = np.array(features)
        
        # Variance (higher is better for discrimination)
        variance = np.var(features_array)
        
        # Range (wider range is better)
        feature_range = np.max(features_array) - np.min(features_array)
        
        # Non-zero features (more non-zero features is better)
        non_zero_count = np.count_nonzero(features_array)
        non_zero_ratio = non_zero_count / len(features_array)
        
        # Calculate quality score (0-1)
        quality_score = (variance * 0.4 + 
                        min(feature_range / 2.0, 1.0) * 0.3 + 
                        non_zero_ratio * 0.3)
        
        return min(quality_score, 1.0)
    
    def assess_person_features(self, person_folder):
        """Assess features for all images of a person"""
        if not os.path.exists(person_folder):
            return None
        
        image_files = [f for f in os.listdir(person_folder) if f.endswith('.jpg')]
        quality_scores = []
        
        for image_file in image_files:
            image_path = os.path.join(person_folder, image_file)
            features = return_128d_features(image_path)
            
            if features != 0:
                quality = self.assess_feature_quality(features)
                quality_scores.append(quality)
                print(f"{image_file}: Quality score = {quality:.3f}")
        
        if quality_scores:
            avg_quality = np.mean(quality_scores)
            print(f"Average quality for {person_folder}: {avg_quality:.3f}")
            return avg_quality
        
        return 0.0

# Usage
if __name__ == '__main__':
    assessor = FeatureQualityAssessor()
    
    # Assess single image
    features = return_128d_features("data/data_faces_from_camera/person_1_john/img_face_1.jpg")
    if features != 0:
        quality = assessor.assess_feature_quality(features)
        print(f"Feature quality: {quality:.3f}")
    
    # Assess person's features
    assessor.assess_person_features("data/data_faces_from_camera/person_1_john")
```

---

## Web Application Examples

### 1. Basic Web Application

```python
from app import app

def run_web_app():
    """Run the web application"""
    app.run(debug=True, host='0.0.0.0', port=5000)

# Usage
if __name__ == '__main__':
    run_web_app()
```

### 2. Custom Web API

```python
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/api/attendance/<date>')
def get_attendance_api(date):
    """API endpoint to get attendance for a specific date"""
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (date,))
        attendance_data = cursor.fetchall()
        
        conn.close()
        
        # Format response
        attendance_list = []
        for name, time in attendance_data:
            attendance_list.append({
                'name': name,
                'time': time
            })
        
        return jsonify({
            'date': date,
            'attendance_count': len(attendance_list),
            'attendance': attendance_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/stats')
def get_attendance_stats():
    """API endpoint to get attendance statistics"""
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get total attendance count
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = cursor.fetchone()[0]
        
        # Get unique persons
        cursor.execute("SELECT COUNT(DISTINCT name) FROM attendance")
        unique_persons = cursor.fetchone()[0]
        
        # Get date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM attendance")
        date_range = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'total_attendance_records': total_attendance,
            'unique_persons': unique_persons,
            'date_range': {
                'start': date_range[0],
                'end': date_range[1]
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Usage
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### 3. Real-time Attendance Dashboard

```python
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

class AttendanceMonitor:
    def __init__(self):
        self.last_check = datetime.now()
    
    def check_new_attendance(self):
        """Check for new attendance records"""
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, time, date 
            FROM attendance 
            WHERE datetime(date || ' ' || time) > datetime(?)
            ORDER BY datetime(date || ' ' || time) DESC
        """, (self.last_check.strftime('%Y-%m-%d %H:%M:%S'),))
        
        new_records = cursor.fetchall()
        conn.close()
        
        if new_records:
            self.last_check = datetime.now()
            return new_records
        
        return []

def monitor_attendance():
    """Background thread to monitor attendance"""
    monitor = AttendanceMonitor()
    
    while True:
        new_records = monitor.check_new_attendance()
        
        if new_records:
            for record in new_records:
                socketio.emit('new_attendance', {
                    'name': record[0],
                    'time': record[1],
                    'date': record[2]
                })
        
        time.sleep(5)  # Check every 5 seconds

@app.route('/dashboard')
def dashboard():
    """Real-time attendance dashboard"""
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to attendance monitor'})

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_attendance, daemon=True)
monitor_thread.start()

# Usage
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5002)
```

---

## Database Operations

### 1. Direct Database Access

```python
import sqlite3
from datetime import datetime, timedelta

class AttendanceDatabase:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_attendance(self, name, time=None, date=None):
        """Add attendance record"""
        if time is None:
            time = datetime.now().strftime('%H:%M:%S')
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                (name, time, date)
            )
            conn.commit()
            print(f"Attendance recorded for {name} on {date} at {time}")
            return True
        except sqlite3.IntegrityError:
            print(f"Attendance already recorded for {name} on {date}")
            return False
        finally:
            conn.close()
    
    def get_attendance_by_date(self, date):
        """Get attendance records for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, time FROM attendance WHERE date = ? ORDER BY time", (date,))
        records = cursor.fetchall()
        
        conn.close()
        return records
    
    def get_attendance_by_person(self, name):
        """Get all attendance records for a person"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT date, time FROM attendance WHERE name = ? ORDER BY date DESC", (name,))
        records = cursor.fetchall()
        
        conn.close()
        return records
    
    def get_attendance_stats(self):
        """Get attendance statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_records = cursor.fetchone()[0]
        
        # Unique persons
        cursor.execute("SELECT COUNT(DISTINCT name) FROM attendance")
        unique_persons = cursor.fetchone()[0]
        
        # Today's attendance
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
        today_attendance = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_records': total_records,
            'unique_persons': unique_persons,
            'today_attendance': today_attendance
        }

# Usage
if __name__ == '__main__':
    db = AttendanceDatabase()
    
    # Add attendance
    db.add_attendance("John Doe")
    
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    records = db.get_attendance_by_date(today)
    print(f"Today's attendance: {records}")
    
    # Get stats
    stats = db.get_attendance_stats()
    print(f"Database stats: {stats}")
```

### 2. Attendance Analytics

```python
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class AttendanceAnalytics:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
    
    def get_attendance_dataframe(self, start_date=None, end_date=None):
        """Get attendance data as pandas DataFrame"""
        conn = sqlite3.connect(self.db_path)
        
        if start_date and end_date:
            query = """
                SELECT name, time, date 
                FROM attendance 
                WHERE date BETWEEN ? AND ?
                ORDER BY date, time
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date, time", conn)
        
        conn.close()
        
        # Convert date and time columns
        df['date'] = pd.to_datetime(df['date'])
        df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'])
        
        return df
    
    def attendance_trends(self, days=30):
        """Analyze attendance trends"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = self.get_attendance_dataframe(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        # Daily attendance counts
        daily_counts = df.groupby('date').size()
        
        # Person attendance frequency
        person_counts = df.groupby('name').size().sort_values(ascending=False)
        
        # Time distribution
        df['hour'] = df['datetime'].dt.hour
        hourly_distribution = df.groupby('hour').size()
        
        return {
            'daily_counts': daily_counts,
            'person_counts': person_counts,
            'hourly_distribution': hourly_distribution
        }
    
    def generate_report(self, days=30):
        """Generate comprehensive attendance report"""
        trends = self.attendance_trends(days)
        
        report = {
            'period_days': days,
            'total_attendance': trends['daily_counts'].sum(),
            'average_daily_attendance': trends['daily_counts'].mean(),
            'most_consistent_attendee': trends['person_counts'].index[0],
            'peak_attendance_hour': trends['hourly_distribution'].idxmax(),
            'total_unique_persons': len(trends['person_counts'])
        }
        
        return report

# Usage
if __name__ == '__main__':
    analytics = AttendanceAnalytics()
    
    # Generate 30-day report
    report = analytics.generate_report(30)
    print("Attendance Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
```

---

## Custom Integration Examples

### 1. Email Notifications

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from attendance_taker import Face_Recognizer

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_attendance_notification(self, person_name, attendance_time):
        """Send email notification for attendance"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = 'admin@company.com'
        msg['Subject'] = f'Attendance Recorded - {person_name}'
        
        body = f"""
        Attendance recorded for {person_name}
        Time: {attendance_time}
        Date: {datetime.now().strftime('%Y-%m-%d')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            print(f"Email notification sent for {person_name}")
        except Exception as e:
            print(f"Failed to send email: {e}")

class AttendanceWithEmail(Face_Recognizer):
    def __init__(self, email_notifier):
        super().__init__()
        self.email_notifier = email_notifier
    
    def attendance(self, name):
        """Override to include email notification"""
        super().attendance(name)
        
        # Send email notification
        current_time = datetime.now().strftime('%H:%M:%S')
        self.email_notifier.send_attendance_notification(name, current_time)

# Usage
if __name__ == '__main__':
    notifier = EmailNotifier('smtp.gmail.com', 587, 'your-email@gmail.com', 'your-password')
    recognizer = AttendanceWithEmail(notifier)
    recognizer.run()
```

### 2. Slack Integration

```python
import requests
from attendance_taker import Face_Recognizer

class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_attendance_notification(self, person_name, attendance_time):
        """Send Slack notification for attendance"""
        message = {
            "text": f"✅ {person_name} has arrived at {attendance_time}",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": "Person",
                            "value": person_name,
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": attendance_time,
                            "short": True
                        },
                        {
                            "title": "Date",
                            "value": datetime.now().strftime('%Y-%m-%d'),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=message)
            if response.status_code == 200:
                print(f"Slack notification sent for {person_name}")
            else:
                print(f"Failed to send Slack notification: {response.status_code}")
        except Exception as e:
            print(f"Error sending Slack notification: {e}")

class AttendanceWithSlack(Face_Recognizer):
    def __init__(self, slack_notifier):
        super().__init__()
        self.slack_notifier = slack_notifier
    
    def attendance(self, name):
        """Override to include Slack notification"""
        super().attendance(name)
        
        current_time = datetime.now().strftime('%H:%M:%S')
        self.slack_notifier.send_attendance_notification(name, current_time)

# Usage
if __name__ == '__main__':
    slack_notifier = SlackNotifier('YOUR_SLACK_WEBHOOK_URL')
    recognizer = AttendanceWithSlack(slack_notifier)
    recognizer.run()
```

---

## Error Handling Examples

### 1. Robust Face Recognition

```python
import logging
from attendance_taker import Face_Recognizer
import cv2

class RobustRecognizer(Face_Recognizer):
    def __init__(self):
        super().__init__()
        self.error_count = 0
        self.max_errors = 10
    
    def process(self, stream):
        """Override process with error handling"""
        try:
            if self.get_face_database():
                while stream.isOpened():
                    try:
                        # ... existing process logic ...
                        self.error_count = 0  # Reset error count on success
                        
                    except cv2.error as e:
                        self.error_count += 1
                        logging.error(f"OpenCV error: {e}")
                        
                        if self.error_count >= self.max_errors:
                            logging.error("Too many errors, stopping recognition")
                            break
                        
                        continue
                        
                    except Exception as e:
                        self.error_count += 1
                        logging.error(f"Unexpected error: {e}")
                        
                        if self.error_count >= self.max_errors:
                            logging.error("Too many errors, stopping recognition")
                            break
                        
                        continue
                        
        except Exception as e:
            logging.error(f"Critical error in recognition process: {e}")
        finally:
            stream.release()
            cv2.destroyAllWindows()

# Usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    robust_recognizer = RobustRecognizer()
    robust_recognizer.run()
```

### 2. Database Error Handling

```python
import sqlite3
from contextlib import contextmanager

class SafeDatabase:
    def __init__(self, db_path='attendance.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def safe_add_attendance(self, name, time=None, date=None):
        """Safely add attendance with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    if time is None:
                        time = datetime.now().strftime('%H:%M:%S')
                    if date is None:
                        date = datetime.now().strftime('%Y-%m-%d')
                    
                    cursor.execute(
                        "INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                        (name, time, date)
                    )
                    conn.commit()
                    print(f"Attendance recorded for {name}")
                    return True
                    
            except sqlite3.IntegrityError:
                print(f"Attendance already recorded for {name}")
                return False
                
            except sqlite3.OperationalError as e:
                retry_count += 1
                print(f"Database operation failed (attempt {retry_count}): {e}")
                
                if retry_count >= max_retries:
                    print("Max retries reached, giving up")
                    return False
                
                time.sleep(1)  # Wait before retry
                
            except Exception as e:
                print(f"Unexpected error: {e}")
                return False
        
        return False

# Usage
if __name__ == '__main__':
    safe_db = SafeDatabase()
    success = safe_db.safe_add_attendance("John Doe")
    if success:
        print("Attendance recorded successfully")
    else:
        print("Failed to record attendance")
```

---

## Performance Optimization Examples

### 1. Optimized Face Recognition

```python
import cv2
import numpy as np
from attendance_taker import Face_Recognizer
import threading
import queue

class OptimizedRecognizer(Face_Recognizer):
    def __init__(self):
        super().__init__()
        self.frame_queue = queue.Queue(maxsize=5)
        self.result_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
    
    def start_processing_thread(self):
        """Start background processing thread"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_frames)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing_thread(self):
        """Stop background processing thread"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
    
    def _process_frames(self):
        """Background thread for frame processing"""
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1)
                # Process frame here
                # ... recognition logic ...
                self.result_queue.put(result)
            except queue.Empty:
                continue
    
    def process(self, stream):
        """Optimized process method with threading"""
        self.start_processing_thread()
        
        try:
            while stream.isOpened():
                ret, frame = stream.read()
                if not ret:
                    break
                
                # Add frame to processing queue
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                
                # Get results from result queue
                try:
                    while not self.result_queue.empty():
                        result = self.result_queue.get_nowait()
                        # Handle result
                        pass
                except queue.Empty:
                    pass
                
        finally:
            self.stop_processing_thread()

# Usage
if __name__ == '__main__':
    optimized_recognizer = OptimizedRecognizer()
    optimized_recognizer.run()
```

### 2. Memory-Efficient Feature Storage

```python
import numpy as np
import pickle
import os

class EfficientFeatureStorage:
    def __init__(self, cache_dir='feature_cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def save_features(self, person_name, features):
        """Save features to disk with compression"""
        cache_file = os.path.join(self.cache_dir, f"{person_name}.pkl")
        
        # Compress features
        compressed_features = {
            'features': features,
            'shape': features.shape,
            'dtype': str(features.dtype)
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(compressed_features, f)
    
    def load_features(self, person_name):
        """Load features from disk"""
        cache_file = os.path.join(self.cache_dir, f"{person_name}.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                compressed_features = pickle.load(f)
            
            return compressed_features['features']
        
        return None
    
    def get_all_features(self):
        """Load all cached features"""
        features_dict = {}
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                person_name = filename[:-4]  # Remove .pkl
                features = self.load_features(person_name)
                if features is not None:
                    features_dict[person_name] = features
        
        return features_dict

# Usage
if __name__ == '__main__':
    storage = EfficientFeatureStorage()
    
    # Save features
    features = np.random.rand(128)
    storage.save_features("john_doe", features)
    
    # Load features
    loaded_features = storage.load_features("john_doe")
    print(f"Loaded features shape: {loaded_features.shape}")
```

This comprehensive examples document provides practical usage scenarios for all the APIs and functions in the facial recognition attendance system, from basic setup to advanced customizations and optimizations.