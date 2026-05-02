from flask import Flask, render_template, request
import cv2
import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
import webbrowser

app = Flask(__name__)

# 👉 image ko browser me dikhane ke liye static folder use karenge
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================= LOAD MODEL =================
path = "images"
images = []
classNames = []

for cl in os.listdir(path):
    img = cv2.imread(f"{path}/{cl}")
    if img is None:
        continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    images.append(gray)
    classNames.append(os.path.splitext(cl)[0])

labels = np.arange(len(images))
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# ================= ATTENDANCE =================
def markAttendance(name):
    file = "attendance.csv"

    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write("Name,Date,Time\n")

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    with open(file, "r+") as f:
        lines = f.readlines()

        for line in lines[1:]:
            data = line.strip().split(",")
            if data[0] == name and data[1] == date:
                return

        f.write(f"{name},{date},{time}\n")

# ================= MAIN ROUTE =================
@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    data = []
    img_path = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            img_path = filepath  # 🔥 preview ke liye

            img = cv2.imread(filepath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                label, confidence = model.predict(face)
                name = classNames[label]

                if confidence < 80:
                    markAttendance(name)
                    message = f"✔ Verified: {name}"

                    if os.path.exists("attendance.csv"):
                        with open("attendance.csv") as f:
                            data = f.readlines()[1:]
                else:
                    message = "✖ Not Matched"
                break
            else:
                message = "No face detected"

    return render_template("index.html", message=message, data=data, img_path=img_path)

# ================= GRAPH =================
@app.route("/graph")
def graph():
    if not os.path.exists("attendance.csv"):
        return "No Data"

    with open("attendance.csv", "r") as f:
        lines = f.readlines()[1:]

    names = [line.split(",")[0] for line in lines if line.strip()]

    if not names:
        return "No Data"

    count = Counter(names)

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    plt.bar(count.keys(), count.values())
    plt.title("Attendance Count")
    plt.xlabel("Name")
    plt.ylabel("Days Present")
    plt.savefig("static/graph.png")
    plt.close()

    return render_template("graph.html")

# ================= RUN =================
if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)