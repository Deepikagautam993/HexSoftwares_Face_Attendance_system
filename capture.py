import cv2
import os
import time

name = input("Enter your name: ")

path = "images"
if not os.path.exists(path):
    os.makedirs(path)

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

count = 0
max_images = 30   # kitni images chahiye
delay = 0.7       # seconds (control speed)

last_capture_time = 0

print("Capturing images... Press 'q' to stop")

while True:
    success, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        current_time = time.time()

        # delay control
        if current_time - last_capture_time > delay:
            count += 1
            face = img[y:y+h, x:x+w]

            file_name = f"{path}/{name}_{count}.jpg"
            cv2.imwrite(file_name, face)

            last_capture_time = current_time
            print(f"Captured {count}")

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.imshow("Capturing Faces", img)

    if cv2.waitKey(1) & 0xFF == ord('q') or count >= max_images:
        break

cap.release()
cv2.destroyAllWindows()

print("Images Captured Successfully!")