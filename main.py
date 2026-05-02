import cv2
import os
import numpy as np
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
            if len(data) >= 2 and data[0] == name and data[1] == date:
                return

        f.write(f"{name},{date},{time}\n")

# ================= GRAPH =================
def show_graph():
    if not os.path.exists("attendance.csv"):
        return

    with open("attendance.csv", "r") as f:
        lines = f.readlines()[1:]

    names = [line.split(",")[0] for line in lines if line.strip()]

    if not names:
        return

    count = Counter(names)

    plt.figure()
    plt.bar(count.keys(), count.values())
    plt.title("Attendance Count")
    plt.xlabel("Name")
    plt.ylabel("Days Present")
    plt.show()

# ================= LOAD DATA =================
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

selected_person = None

# ================= FUNCTIONS =================
def set_person(name):
    global selected_person
    selected_person = name
    selected_label.configure(text=f"Selected: {name}")

def load_attendance():
    for widget in table_frame.winfo_children():
        widget.destroy()

    if not os.path.exists("attendance.csv"):
        return

    with open("attendance.csv", "r") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        return

    headers = ["Name", "Date", "Time"]
    for col, h in enumerate(headers):
        ctk.CTkLabel(table_frame, text=h, font=("Arial", 14, "bold")).grid(
            row=0, column=col, padx=15, pady=8
        )

    row_index = 1

    for line in lines[1:]:
        data = line.strip().split(",")

        if len(data) != 3:
            continue

        for col, value in enumerate(data):
            ctk.CTkLabel(table_frame, text=value).grid(
                row=row_index, column=col, padx=15, pady=5
            )

        row_index += 1

    count_label.configure(text=f"Total: {row_index-1}")

def upload_and_check():
    if selected_person is None:
        status_label.configure(text="⚠ Select person first", text_color="orange")
        return

    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    # preview
    img_preview = Image.open(file_path)
    img_preview = img_preview.resize((250, 250))
    preview_img = ctk.CTkImage(light_image=img_preview, size=(250, 250))
    preview_label.configure(image=preview_img, text="")

    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        label, confidence = model.predict(face)
        detected_name = classNames[label]

        if detected_name == selected_person and confidence < 80:
            status_label.configure(text="✔ VERIFIED", text_color="#00FFAA")
            markAttendance(detected_name)
            load_attendance()
        else:
            status_label.configure(text="✖ NOT MATCHED", text_color="#FF4C4C")
        return

    status_label.configure(text="No face detected", text_color="red")

# ================= UI =================
app = ctk.CTk()
app.geometry("1100x620")
app.title("Face Attendance Dashboard")

# ===== SIDEBAR =====
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="AI PANEL", font=("Arial", 20, "bold")).pack(pady=20)

count_label = ctk.CTkLabel(sidebar, text="Total: 0")
count_label.pack(pady=10)

graph_btn = ctk.CTkButton(sidebar, text="Show Graph", command=show_graph)
graph_btn.pack(pady=10)

# ===== MAIN =====
main = ctk.CTkFrame(app)
main.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# ===== HEADER =====
header = ctk.CTkFrame(main, fg_color="#111827")
header.pack(fill="x", pady=10)

ctk.CTkLabel(
    header,
    text="FACE ATTENDANCE DASHBOARD",
    font=("Arial", 20, "bold"),
    text_color="#00FFFF"
).pack(pady=10)

# ===== TOP SECTION =====
top = ctk.CTkFrame(main)
top.pack(fill="x", pady=10)

# ===== LEFT CARD =====
left = ctk.CTkFrame(top, width=400)
left.pack(side="left", padx=15, pady=10)

dropdown = ctk.CTkOptionMenu(left, values=classNames, command=set_person)
dropdown.pack(pady=10)

selected_label = ctk.CTkLabel(left, text="Selected: None")
selected_label.pack()

preview_label = ctk.CTkLabel(left, text="Upload Preview", width=250, height=250)
preview_label.pack(pady=15)

upload_btn = ctk.CTkButton(left, text="Upload & Verify", command=upload_and_check)
upload_btn.pack(pady=10)

status_label = ctk.CTkLabel(left, text="Status: Waiting")
status_label.pack(pady=10)

# ===== RIGHT CARD (TABLE) =====
right = ctk.CTkFrame(top)
right.pack(side="right", fill="both", expand=True, padx=15, pady=10)

ctk.CTkLabel(right, text="Attendance", font=("Arial", 16, "bold")).pack(pady=5)

table_frame = ctk.CTkFrame(right)
table_frame.pack(padx=10, pady=10, fill="both", expand=True)

app.mainloop()