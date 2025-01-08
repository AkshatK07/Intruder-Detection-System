from flask import Flask, send_from_directory, render_template, abort
import os

app = Flask(__name__)

# Paths to logs
BASE_DIR = os.path.join(os.path.expanduser("~/Desktop"), "IDS", "logs")
INTRUDER_IMAGES_DIR = os.path.join(BASE_DIR, "intruder_images")
SCREEN_RECORDINGS_DIR = os.path.join(BASE_DIR, "screen_recordings")

# Ensure directories exist
os.makedirs(INTRUDER_IMAGES_DIR, exist_ok=True)
os.makedirs(SCREEN_RECORDINGS_DIR, exist_ok=True)

@app.route("/")
def home():
    """
    Renders the home page with lists of intruder images and screen recordings.
    """
    try:
        intruder_images = os.listdir(INTRUDER_IMAGES_DIR)
        screen_recordings = os.listdir(SCREEN_RECORDINGS_DIR)
    except FileNotFoundError:
        intruder_images = []
        screen_recordings = []
    return render_template("index.html", images=intruder_images, recordings=screen_recordings)

@app.route("/view/<log_type>/<filename>")
def view_log(log_type, filename):
    """
    Serves the requested log file for viewing.
    """
    folder = None
    if log_type == "images":
        folder = INTRUDER_IMAGES_DIR
    elif log_type == "recordings":
        folder = SCREEN_RECORDINGS_DIR

    if folder and os.path.exists(os.path.join(folder, filename)):
        return send_from_directory(folder, filename)
    else:
        abort(404)

@app.route("/download/<log_type>/<filename>")
def download_log(log_type, filename):
    """
    Serves the requested log file for download.
    """
    folder = None
    if log_type == "images":
        folder = INTRUDER_IMAGES_DIR
    elif log_type == "recordings":
        folder = SCREEN_RECORDINGS_DIR

    if folder and os.path.exists(os.path.join(folder, filename)):
        return send_from_directory(folder, filename, as_attachment=True)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
