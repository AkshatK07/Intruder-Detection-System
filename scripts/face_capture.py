import cv2
import os

def capture_faces():
    # Set base directory for datasets
    base_dir = os.path.join(os.path.expanduser("~/Desktop"), "IDS")
    dataset_path = os.path.join(base_dir, "datasets")

    # Create dataset directory if it doesn't exist
    os.makedirs(dataset_path, exist_ok=True)

    user_name = input("Enter the name of the new authorized user: ").strip()
    user_folder = os.path.join(dataset_path, user_name)

    # Create user folder if it doesn't exist
    os.makedirs(user_folder, exist_ok=True)

    # Initialize webcam and face detector
    camera = cv2.VideoCapture(0)
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

    if not os.path.exists(face_cascade_path):
        print(f"Error: Haarcascade file not found at {face_cascade_path}")
        return

    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    if not camera.isOpened():
        print("Error: Unable to access the camera.")
        return

    print(f"Capturing face images for {user_name}. Press 'q' to quit.")
    count = 0

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Unable to capture frame from the camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            file_name = os.path.join(user_folder, f"{count}.jpg")
            cv2.imwrite(file_name, face)
            count += 1
            print(f"Captured face {count}: {file_name}")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Face Capture", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            confirm_exit = input("Are you sure you want to quit? (y/n): ").strip().lower()
            if confirm_exit == 'y':
                break

    camera.release()
    cv2.destroyAllWindows()
    print(f"Face capture complete. Total images: {count}")
    print(f"Images saved in: {user_folder}")

if __name__ == "__main__":
    capture_faces()
