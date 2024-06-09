import cv2
import threading

# Load the face recognizer and cascade classifier once
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('traines/trainer.yml')
cascadePath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath)

# Define font for text
font = cv2.FONT_HERSHEY_SIMPLEX

# List of names corresponding to IDs
names = ['', 'avi', 'roshan']

# Initialize the video capture
cam = cv2.VideoCapture(0, cv2.CAP_MSMF)  # Use CAP_MSMF backend for DroidCam
if not cam.isOpened():
    cam = cv2.VideoCapture(0, cv2.CAP_ANY)  # Fallback to CAP_ANY (auto-detect)
    if not cam.isOpened():
        print("Error: Unable to open DroidCam.")
        exit()

# Set video frame width and height
cam.set(3, 640)
cam.set(4, 480)

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

def process_frame():
    while True:
        ret, img = cam.read()
        if not ret:
            print("Error: Unable to read frame from DroidCam.")
            break

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(converted_image, scaleFactor=1.2, minNeighbors=5,
                                             minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id_, accuracy = recognizer.predict(converted_image[y:y + h, x:x + w])

            if accuracy < 100:
                name = names[id_] if id_ < len(names) else "Unknown"
                accuracy = f" ({round(100 - accuracy)}%)"
            else:
                name = "Unknown"
                accuracy = f" ({round(100 - accuracy)}%)"

            cv2.putText(img, str(name), (x, y - 10), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(accuracy), (x, y + h + 20), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

# Use a separate thread for processing frames
thread = threading.Thread(target=process_frame)
thread.start()
thread.join()

print("Thanks for using this program, have a good day.")
