# Facial Recognition Attendance System

This project implements a facial recognition attendance system using Python. It allows users to register new faces, recognize them in real-time, and log attendance based on facial recognition. The system provides a user-friendly interface for managing attendance records.

## Project Structure

- **main.py**: This script is used to register new faces and capture images.
- **attendance_taker.py**: This script recognizes faces, trains the model, and logs attendance for the current date.
- **app.py**: This application allows users to view their attendance records by selecting a specific date.
- **resources/**: This directory contains the necessary Dlib binary `.whl` files required to install Dlib for the project.
- **requirements.txt**: A file listing all the necessary Python packages and their versions required to run the project.

## Features

- **Face Registration**: Users can register new faces by capturing images through the webcam.
- **Real-Time Recognition**: The system can recognize registered faces in real-time and log attendance.
- **Attendance Logging**: Attendance is recorded with timestamps for each recognized face.
- **View Attendance Records**: Users can view their attendance records by selecting a date.

## Installation

To set up this project locally, follow these steps:

1. **Clone the Repository**:
**`git clone https://github.com/yourusername/attendance-system.git`**
**`cd attendance-system`**


2. **Create a Virtual Environment (Optional but Recommended)**:
`python -m venv env_name`
`source venv/bin/activate` # On Windows use `venv\Scripts\activate`


3. **Install Required Packages**:
Install the required packages using the provided `requirements.txt` file:
`pip install -r requirements.txt`


4. **Install Dlib**:
If you are using Windows, you may need to install Dlib from the provided `.whl` files in the `resources` directory. Use the following command:
`pip install resources/dlib-<version>.whl` # Replace <version> with the actual file name


## Download Necessary Files

To run the code in this project, you will need to download the necessary files from Google Drive. Click the link below to access the files:

[Download Required Files](https://drive.google.com/drive/folders/1MJ86CfAg3ZfjAhHwn8-BoqdpIqsxah25?usp=sharing)

### Instructions

1. Click the link above to open the Google Drive folder.
2. Download all files by selecting them and clicking on the download icon.
3. Place the downloaded files in the appropriate directory as specified in the project documentation.

If you encounter any issues while downloading or running the code, please refer to the troubleshooting section or open an issue on this repository.



## Usage

1. **Register New Faces**:
Run `main.py` to start registering new faces.
**`python main.py`**


2. **Take Attendance**:
After registering faces, run `attendance_taker.py` to recognize faces and log attendance.
***`python attendance_taker.py`***


3. **View Attendance Records**:
Use `app.py` to view your attendance records by selecting a specific date.
***`python app.py`***


## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to [Dlib](http://dlib.net/) for providing robust face detection and recognition capabilities.
- Thanks to [OpenCV](https://opencv.org/) for image processing functionalities.

