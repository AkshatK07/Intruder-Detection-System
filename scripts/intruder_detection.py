import cv2
import os
import datetime
import time
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client

# Base directories
BASE_DIR = os.path.join(os.path.expanduser("~/Desktop"), "IDS")
MODEL_PATH = os.path.join(BASE_DIR, "face_model.yml")
LABEL_MAPPING_PATH = os.path.join(BASE_DIR, "label_mapping.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
INTRUDER_IMAGES_DIR = os.path.join(LOG_DIR, "intruder_images")
os.makedirs(INTRUDER_IMAGES_DIR, exist_ok=True)

# Load the model and label mapping
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
if not os.path.exists(LABEL_MAPPING_PATH):
    raise FileNotFoundError(f"Label mapping file not found: {LABEL_MAPPING_PATH}")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

with open(LABEL_MAPPING_PATH, "r") as file:
    label_dict = json.load(file)

# Haarcascade for face detection
HAARCASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
if not os.path.exists(HAARCASCADE_PATH):
    raise FileNotFoundError(f"Haarcascade file not found: {HAARCASCADE_PATH}")
face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")  # Replace for testing
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")  # Replace for testing
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Replace for testing

# Twilio WhatsApp Configuration
ACCOUNT_SID = ""  # Replace with your Twilio Account SID
AUTH_TOKEN = ""    # Replace with your Twilio Auth Token
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio's Sandbox Number
RECIPIENT_WHATSAPP_NUMBER = "whatsapp:+91"  # Replace with your number

# Cooldown configuration
last_alert_time = {}  # Tracks cooldown per face ID
ALERT_COOLDOWN = 30  # Cooldown period in seconds

# Function to send WhatsApp messages
def send_whatsapp_message(image_path, message_body):
    """
    Sends a WhatsApp message with an optional image attachment.
    """
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    image_host_url = "https://your_public_hosting_url.com/" + os.path.basename(image_path)  # Public image URL
    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=RECIPIENT_WHATSAPP_NUMBER,
            media_url=[image_host_url]
        )
        print(f"WhatsApp message sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

# Function to send email
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
        print(f"Failed to send email: {e}")

# Function to save intruder image
def save_intruder_image(frame):
    """
    Saves the detected intruder's image to the logs directory.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    intruder_image_path = os.path.join(INTRUDER_IMAGES_DIR, f"intruder_{timestamp}.jpg")
    cv2.imwrite(intruder_image_path, frame)
    return intruder_image_path

# Function to handle intruders
def handle_intruder(face_id, frame):
    """
    Handles actions when an intruder is detected.
    """
    global last_alert_time
    current_time = time.time()

    # Check cooldown for this face
    if face_id in last_alert_time and current_time - last_alert_time[face_id] < ALERT_COOLDOWN:
        print(f"Cooldown active for face {face_id}. Skipping alert.")
        return

    # Update last alert time for this face
    last_alert_time[face_id] = current_time

    print(f"Intruder detected! Face ID: {face_id}")
    intruder_image_path = save_intruder_image(frame)

    # Send an email alert
    send_email(
        subject=f"Intruder Alert: Face ID {face_id}",
        body="An unauthorized person has been detected. See the attached image for details.",
        attachment_path=intruder_image_path
    )

    # Send a WhatsApp alert
    send_whatsapp_message(
        image_path=intruder_image_path,
        message_body="Alert! An intruder has been detected. See the attached image."
    )

# Detect faces
def detect_faces():
    """
    Detects and recognizes multiple faces using a webcam.
    """
    camera = cv2.VideoCapture(0)
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

        for face_id, (x, y, w, h) in enumerate(faces):
            face = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face)

            if confidence < 50:  # Recognized face
                user_name = label_dict.get(str(label), "Unknown")
                print(f"Recognized: {user_name} (Face ID: {face_id}, Confidence: {confidence:.2f})")
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f"{user_name} ({confidence:.2f})", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:  # Intruder detected
                print(f"Unrecognized face detected (Face ID: {face_id})")
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)  # Red rectangle
                cv2.putText(frame, "Intruder", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                handle_intruder(face_id, frame)

        cv2.imshow("Intruder Detection", frame)

        # Quit detection loop on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("Camera released.")

if __name__ == "__main__":
    detect_faces()
