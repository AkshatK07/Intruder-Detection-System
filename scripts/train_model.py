import cv2
import numpy as np
import os

def train_model():
    # Set base directory to IDS folder on the desktop
    base_dir = os.path.join(os.path.expanduser("~/Desktop"), "IDS")
    base_dataset_path = os.path.join(base_dir, "datasets/")
    model_path = os.path.join(base_dir, "face_model.yml")

    if not os.path.exists(base_dataset_path):
        raise FileNotFoundError(f"Dataset folder not found at {base_dataset_path}. Please create it and add user images.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    images, labels = [], []
    label_dict = {}

    for label, user_name in enumerate(os.listdir(base_dataset_path)):
        user_folder = os.path.join(base_dataset_path, user_name)
        print(f"Processing folder: {user_folder}")  # Debugging
        for filename in os.listdir(user_folder):
            img_path = os.path.join(user_folder, filename)
            print(f"Found file: {img_path}")  # Debugging
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images.append(img)
                labels.append(label)
        label_dict[label] = user_name

    if not images:
        raise ValueError(f"No images found in dataset folder: {base_dataset_path}. Ensure that each user folder contains image files.")

    # Train and save model
    recognizer.train(images, np.array(labels))
    recognizer.save(model_path)
    print(f"Model trained and saved to {model_path}. User mapping: {label_dict}")

if __name__ == "__main__":
    train_model()
