import cv2
import pyautogui
import numpy as np
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time

# Base directory: IDS folder on the desktop
BASE_DIR = os.path.join(os.path.expanduser("~/Desktop"), "IDS")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets/")
LOG_DIR = os.path.join(BASE_DIR, "logs/")
SCREEN_RECORDINGS_DIR = os.path.join(LOG_DIR, "screen_recordings/")
INTRUDER_IMAGES_DIR = os.path.join(LOG_DIR, "intruder_images/")

# Create necessary directories
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(SCREEN_RECORDINGS_DIR, exist_ok=True)
os.makedirs(INTRUDER_IMAGES_DIR, exist_ok=True)

# Load the face recognition model
MODEL_PATH = r"C:\Users\arnav\Desktop\IDS\face_model.yml"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found.")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

# Haarcascade for face detection
HAARCASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
if not os.path.exists(HAARCASCADE_PATH):
    raise FileNotFoundError(f"Haarcascade file '{HAARCASCADE_PATH}' not found.")
face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)

# Email Configuration
EMAIL_SENDER = "akshatkansara07@gmail.com"
EMAIL_RECEIVER = "arnavkansara3@gmail.com"
EMAIL_PASSWORD = "micibwqzsngiudek"  # App password, not your email password

# Cooldown Variables
last_alert_time = 0  # Tracks the last time an alert was sent
ALERT_COOLDOWN = 30  # Cooldown period in seconds


def send_email(subject, body, attachment_path=None):
    """
    Sends an email with optional attachment.
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}"
        )
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def record_screen(duration=10):
    """
    Records the screen for the specified duration and saves it to the logs directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(SCREEN_RECORDINGS_DIR, f"screen_{timestamp}.avi")
    screen_size = pyautogui.size()
    fps = 10.0

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, fps, screen_size)

    print(f"Recording screen: {output_file}")
    try:
        for _ in range(int(fps * duration)):
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB)
            out.write(frame)
    finally:
        out.release()
        print("Screen recording saved.")


def save_intruder_image(frame):
    """
    Saves the detected intruder's image to the logs directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    intruder_image_path = os.path.join(INTRUDER_IMAGES_DIR, f"intruder_{timestamp}.jpg")
    cv2.imwrite(intruder_image_path, frame)
    return intruder_image_path


def intruder_actions(frame):
    """
    Handles actions triggered when an intruder is detected.
    """
    global last_alert_time
    current_time = time.time()

    # Check if the cooldown period has passed
    if current_time - last_alert_time < ALERT_COOLDOWN:
        print("Cooldown active. Skipping alert.")
        return  # Skip sending another alert

    last_alert_time = current_time  # Update the last alert time

    try:
        print("Recording screen and capturing intruder image...")
        record_screen(duration=10)
        intruder_image_path = save_intruder_image(frame)
        send_email(
            subject="Intruder Alert!",
            body="An unauthorized person was detected. See the attached image for details.",
            attachment_path=intruder_image_path
        )
    except Exception as e:
        print(f"Error during intruder actions: {e}")


def detect_intruders():
    """
    Main function for detecting intruders using a webcam.
    """
    authorized_label = 0  # Replace with your authorized user label
    authorized_name = "Akshat"  # Replace with your name
    camera = cv2.VideoCapture(0)  # Ensure the correct camera index

    if not camera.isOpened():
        print("Error: Unable to access the camera.")
        return

    print("Intruder Detection System Started. Press 'q' to exit.")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face)

            if label == authorized_label and confidence < 50:  # Recognized authorized user
                print(f"Authorized user detected: {authorized_name}")
                # Draw green rectangle with name tag
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(
                    frame,
                    f"{authorized_name} (Confidence: {confidence:.2f})",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),  # Green text
                    2,
                )
            else:  # Intruder detected
                print("Intruder detected!")
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)  # Red rectangle
                cv2.putText(
                    frame,
                    f"Intruder (Confidence: {confidence:.2f})",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),  # Red text
                    2,
                )
                intruder_actions(frame)  # Handle intruder actions
                break  # Avoid duplicate actions for the same frame

        cv2.imshow("Intruder Detection", frame)

        # Quit the detection loop on 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting detection...")
            break

    camera.release()
    cv2.destroyAllWindows()
    print("Camera released.")


if __name__ == "__main__":
    detect_intruders()
