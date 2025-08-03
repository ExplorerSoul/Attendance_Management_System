# Facial Recognition Attendance System

A robust facial recognition attendance system built with Python, Flask, and Docker. This system allows users to register faces, recognize them in real-time, and manage attendance records through a modern web interface.

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd attendance-system

# Deploy with one command
./deploy.sh

# Access the application
open http://localhost
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5000
```

## 📁 Project Structure

```
attendance-system/
├── app.py                 # Flask web application
├── main.py               # Face registration script
├── attendance_taker.py   # Face recognition and attendance logging
├── templates/            # HTML templates
├── data/                 # Face data and models
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container deployment
├── nginx.conf          # Reverse proxy configuration
└── deploy.sh           # Automated deployment script
```

## ✨ Features

- **🔐 Face Registration**: Register new faces through webcam capture
- **👁️ Real-Time Recognition**: Instant face recognition and attendance logging
- **📊 Web Dashboard**: Modern web interface for viewing attendance records
- **🐳 Docker Ready**: Containerized deployment with Docker
- **🔧 Production Ready**: Nginx reverse proxy, health checks, and monitoring
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🛠️ Installation & Setup

### Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.8+ (for local development)
- Webcam (for face registration and recognition)

### Download Required Files

Before running the application, download the required Dlib model files:

1. **Download from Google Drive**: [Required Files](https://drive.google.com/drive/folders/1MJ86CfAg3ZfjAhHwn8-BoqdpIqsxah25?usp=sharing)
2. **Place files in**: `data/data_dlib/`
   - `shape_predictor_68_face_landmarks.dat`
   - `dlib_face_recognition_resnet_model_v1.dat`

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Quick deployment
./deploy.sh

# Or manual deployment
docker-compose up -d
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📖 Usage

### 1. Face Registration

```bash
python main.py
```

- Follow the on-screen instructions
- Enter the person's name
- Capture face images through the webcam
- The system will save face features for recognition

### 2. Attendance Taking

```bash
python attendance_taker.py
```

- The system will automatically detect and recognize registered faces
- Attendance is logged with timestamps
- Data is stored in SQLite database

### 3. View Attendance Records

- Open the web application at `http://localhost:5000`
- Select a date to view attendance records
- View detailed attendance data in a clean table format

## 🧪 Testing

```bash
# Run the test suite
python test_app.py

# Or use Makefile
make test
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost/health
```

### Application Status

```bash
make status
```

## 🔧 Management Commands

```bash
# View all available commands
make help

# Start the application
make run

# Stop the application
make stop

# View logs
make logs

# Backup database
make backup

# Update application
make update
```

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

## 🔒 Security Considerations

- Change the default secret key in production
- Use HTTPS in production environments
- Set up proper firewall rules
- Regularly update dependencies
- Backup database regularly

## 📈 Production Deployment

For production deployment, consider:

- Using a production database (PostgreSQL/MySQL)
- Setting up SSL/TLS certificates
- Implementing proper logging and monitoring
- Using a load balancer for high availability
- Setting up automated backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Dlib](http://dlib.net/) - Face detection and recognition
- [OpenCV](https://opencv.org/) - Computer vision library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - UI framework

## 📞 Support

For support and questions:
- Check the [Deployment Guide](DEPLOYMENT.md)
- Review the troubleshooting section
- Open an issue on GitHub

