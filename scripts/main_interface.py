from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
import os
import subprocess

class IntruderDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intruder Detection System")
        self.setGeometry(100, 100, 500, 400)

        # Buttons
        start_btn = QPushButton("Start Intruder Detection", self)
        start_btn.clicked.connect(self.start_detection)

        register_face_btn = QPushButton("Register New Face", self)
        register_face_btn.clicked.connect(self.register_new_face)

        train_model_btn = QPushButton("Train Model", self)
        train_model_btn.clicked.connect(self.train_model)

        test_email_btn = QPushButton("Test Email Alert", self)
        test_email_btn.clicked.connect(self.test_email)

        test_whatsapp_btn = QPushButton("Test WhatsApp Notification", self)
        test_whatsapp_btn.clicked.connect(self.test_whatsapp)

        view_logs_btn = QPushButton("View Logs", self)
        view_logs_btn.clicked.connect(self.view_logs)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(start_btn)
        layout.addWidget(register_face_btn)
        layout.addWidget(train_model_btn)
        layout.addWidget(test_email_btn)
        layout.addWidget(test_whatsapp_btn)
        layout.addWidget(view_logs_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_detection(self):
        """
        Starts the intruder detection process.
        """
        detection_script = os.path.abspath(r"C:/Users/arnav/Desktop/IDS/scripts/intruder_detection.py")
        print(f"Resolved detection script path: {detection_script}")

        if os.path.exists(detection_script):
            subprocess.Popen(["python", detection_script])
            self.show_message("Intruder Detection Started")
        else:
            self.show_message(f"Script not found: {detection_script}")

    def register_new_face(self):
        """
        Opens the face registration script to capture new face data.
        """
        register_script = os.path.abspath(r"C:/Users/arnav/Desktop/IDS/scripts/capture_faces.py")
        print(f"Resolved face registration script path: {register_script}")

        if os.path.exists(register_script):
            subprocess.Popen(["python", register_script])
            self.show_message("Face registration started. Follow the prompts.")
        else:
            self.show_message(f"Script not found: {register_script}")

    def train_model(self):
        """
        Runs the model training script to update the face recognizer.
        """
        train_script = os.path.abspath(r"C:/Users/arnav/Desktop/IDS/scripts/train_model.py")
        print(f"Resolved training script path: {train_script}")

        if os.path.exists(train_script):
            subprocess.Popen(["python", train_script])
            self.show_message("Model training started. Please wait.")
        else:
            self.show_message(f"Script not found: {train_script}")

    def test_email(self):
        """
        Test email alert functionality.
        """
        test_script = """
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
    print("Email credentials are not set.")
else:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "Test Email from IDS"
    msg.attach(MIMEText("This is a test email from the Intruder Detection System.", "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Test email sent successfully.")
    except Exception as e:
        print(f"Error sending test email: {e}")
"""
        with open("test_email.py", "w") as file:
            file.write(test_script)

        test_email_script = os.path.abspath("test_email.py")
        subprocess.Popen(["python", test_email_script])

    def test_whatsapp(self):
        """
        Test WhatsApp notification functionality.
        """
        test_script = """
from twilio.rest import Client

ACCOUNT_SID = ""
AUTH_TOKEN = ""
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
RECIPIENT_WHATSAPP_NUMBER = "whatsapp:+91"

def send_test_whatsapp_message():
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        message = client.messages.create(
            body="This is a test WhatsApp message from the Intruder Detection System.",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=RECIPIENT_WHATSAPP_NUMBER
        )
        print(f"WhatsApp test message sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp test message: {e}")

send_test_whatsapp_message()
"""
        with open("test_whatsapp.py", "w") as file:
            file.write(test_script)

        test_whatsapp_script = os.path.abspath("test_whatsapp.py")
        subprocess.Popen(["python", test_whatsapp_script])

    def view_logs(self):
        """
        Opens the logs directory in File Explorer.
        """
        log_dir = os.path.join(os.path.expanduser("~/Desktop"), "IDS", "logs")
        if os.path.exists(log_dir):
            try:
                os.startfile(log_dir)  # For Windows
            except Exception as e:
                self.show_message(f"Unable to open logs folder: {e}")
        else:
            self.show_message("Logs folder does not exist.")

    def show_message(self, message):
        """
        Displays a popup message to the user.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        msg_box.exec_()

def main():
    app = QApplication([])
    main_window = IntruderDetectionApp()
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
