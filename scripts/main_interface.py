from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
import os
import subprocess

class IntruderDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intruder Detection System")
        self.setGeometry(100, 100, 400, 300)

        # Buttons
        start_btn = QPushButton("Start Intruder Detection", self)
        start_btn.clicked.connect(self.start_detection)

        view_logs_btn = QPushButton("Open Detection Logs", self)
        view_logs_btn.clicked.connect(self.view_logs)

        add_user_btn = QPushButton("Register New User", self)
        add_user_btn.clicked.connect(self.add_user)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(start_btn)
        layout.addWidget(view_logs_btn)
        layout.addWidget(add_user_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def start_detection(self):
        detection_script = "C:/Users/arnav/Desktop/IDS/scripts/intruder_detection.py"
        if os.path.exists(detection_script):
            subprocess.Popen(["python", detection_script])
            self.show_message("Intruder Detection Started")
            self.status_bar.showMessage("Intruder Detection Running")
        else:
            self.show_message(f"Script not found: {detection_script}")

    def view_logs(self):
        log_dir = os.path.abspath("./logs/")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        try:
            os.startfile(log_dir)
        except Exception as e:
            self.show_message(f"Unable to open logs folder: {e}")

    def add_user(self):
        capture_script = "C:/Users/arnav/Desktop/IDS/scripts/face_capture.py"
        if os.path.exists(capture_script):
            subprocess.Popen(["python", capture_script])
            self.show_message("Capture New User's Face")
        else:
            self.show_message(f"Script not found: {capture_script}")

    def show_message(self, message):
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
