# 📸 Advanced Facial Recognition Attendance System

This project is an **advanced, scalable, and real-time Facial Recognition Attendance System** built with Python.  
It utilizes a **modular, microservices-inspired architecture** incorporating a message queue for asynchronous processing and WebSockets for instant frontend updates.

---

## ✨ Highlights & Key Features

- **🖥️ Real-Time Dashboard:**  
  Attendance events are instantly pushed to the web dashboard using WebSockets, providing immediate feedback.

- **⚙️ Asynchronous Processing:**  
  Implements a Producer/Consumer architecture (via a Message Queue) to offload heavy tasks like face feature extraction, preventing UI lag and ensuring scalability.

- **🎯 High-Fidelity Recognition:**  
  Leverages the Dlib library for highly accurate facial detection and embedding generation.

- **🧠 Spoofing Prevention:**  
  Includes a Liveness Detection module (`liveness.py`) to prevent fraudulent attendance logging using photos or videos.

- **💾 Data Persistence:**  
  Attendance and user records are managed through a robust backend database (configured via `db_config.py`).

- **🧩 Modular Design:**  
  Clear separation of concerns into dedicated files for registration, recognition, utility, and database management.

---

## ⚙️ Tech Stack and Architecture

This project is built primarily on **Python** and integrates several powerful technologies to achieve **real-time, asynchronous functionality**.

| **Category** | **Technology** | **Implied Role** |
|--------------|----------------|------------------|
| Backend & Core | Python 3.x | Core programming language |
| Web Framework | Flask / Django Channels (via `app.py`) | Serving API endpoints and handling WebSocket connections |
| Computer Vision | Dlib, OpenCV (`cv2`) | Facial recognition, detection, and image processing |
| Asynchronous Processing | Message Queue (Redis / RabbitMQ) | Decouples recognition service (producer) from feature extraction/DB update worker (consumer) |
| Real-Time Communication | WebSockets | Pushes live attendance logs and recognition status to frontend |
| Database | SQL/NoSQL (via `init_db.py`) | Stores user data, face embeddings, and attendance logs |

---

## 📂 Project Structure

```bash
Attendance_Management_System/
├── data/                        # Stores raw attendance logs, database files, or features
├── dlib/                        # Dlib-related files (e.g., trained models)
├── media/                       # Stores registered user images for training
├── requirements/
│   ├── dlib_binary_files.whl    # Pre-compiled Dlib binary for easier installation
│   └── requirements.txt         # All necessary Python dependencies
├── templates/
│   └── index.html               # Frontend web dashboard template
├── .env                         # Environment variables for configuration
├── app.py                       # Main web application entry point (Flask/Django)
├── attendance_taker.py          # Real-time face recognition and attendance logging
├── ca.pem                       # Certificate file (for secure WebSocket/API communication)
├── config.py                    # Centralized configuration settings
├── consumer_worker.py           # Worker that processes tasks from the message queue
├── db_config.py                 # Database configuration and setup
├── face_register.py             # Script for registering new user faces
├── face_utils.py                # Common utilities for face processing
├── features_extraction_to_csv.py # Generates face embeddings from raw images
├── init_db.py                   # Initializes the database schema and tables
├── liveness.py                  # Liveness/spoofing detection module
├── producer_service.py          # Sends recognition/registration requests to the message queue
└── LICENSE, README.md, etc.
````

---

## 🛠️ Installation and Setup

### 1. Prerequisites

* **Python 3.8+**
* **Git**
* A running **Message Queue instance** (Redis or RabbitMQ or Valkey)

---

### 2. Clone the Repository

```bash
git clone https://github.com/ExplorerSoul/Attendance_Management_System.git
```

---

### 3. Setup Virtual Environment

It’s highly recommended to use a virtual environment.

```bash
python -m venv env

# Activate the environment
# macOS/Linux
source env/bin/activate

# Windows
env\Scripts\activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements/requirements.txt
```

If you encounter issues installing Dlib, use the pre-compiled binary:

```bash
pip install requirements/dlib_binary_files.whl
```

---

### 5. Configuration and Initialization

#### Create `.env` File

Create a `.env` file in the root directory based on the variables required in `config.py`.

Example configuration:

```bash
MQ_URL=redis://localhost:6379/0
DB_URL=sqlite:///./data/attendance.db
SECRET_KEY=your_secure_secret
```

#### Initialize Database

```bash
python init_db.py
```

---

## ▶️ Usage Guide

To run the full system, you need to start the **Web Application**, **Consumer Worker**, **Producer Service**, and **Attendance Taker** concurrently.

### Step 1: Start the Consumer Worker (MQ Listener)

```bash
python consumer_worker.py
```

This worker listens to the message queue and processes tasks like saving new features or updating the database.

---

### Step 2: Start the Web Application (API & WebSockets)

```bash
python app.py
```

This runs the server, which hosts the dashboard and manages real-time WebSocket connections.

---

### Step 3: Register New Users

```bash
python face_register.py
```

Uses the webcam to capture new faces and sends registration data to the message queue.

---

### Step 4: Extract Features

```bash
python features_extraction_to_csv.py
```

Processes the captured images into face embeddings and saves them for recognition.

---

### Step 5: Start Real-Time Attendance

```bash
python attendance_taker.py
```

Launches webcam recognition and sends attendance events through the message queue to update the dashboard live.

---

## 🤝 Contributing

Contributions are welcome!
If you find a bug or have suggestions, please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](./LICENSE) file for details.

---

### 💡 Future Enhancements

* Cloud-based face embedding storage for scalability
* Multi-camera support for large environments
* Enhanced UI for attendance analytics
* Integration with biometric hardware
* Edge computing support for offline recognition

```
