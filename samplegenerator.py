import cv2
import threading

# Reduce frame size for faster processing
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Function to initialize the camera with different backends
def init_camera(cam_id):
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW, cv2.CAP_ANY]
    for backend in backends:
        cam = cv2.VideoCapture(cam_id, backend)
        if cam.isOpened():
            print(f"Camera opened successfully with backend {backend}")
            return cam
        else:
            print(f"Failed to open camera with backend {backend}")
    return None

# Initialize video capture with the identified camera ID and available backends
CAM_DEVICE_ID = 0 # Adjust based on your setup

cam = init_camera(CAM_DEVICE_ID)
if cam is None or not cam.isOpened():
    print(f"Error: Unable to open camera with ID {CAM_DEVICE_ID} using all tried backends.")
    exit()

cam.set(3, FRAME_WIDTH)
cam.set(4, FRAME_HEIGHT)

# Initialize the face detector
detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Get user ID
face_id = input("Enter a numeric userid here: ")

print("Taking samples, look at the camera.")
count = 0

# Function to save image in a separate thread
def save_image(img, face_id, count):
    cv2.imwrite(f"Samples/face.{face_id}_{count}.jpg", img)

# Main loop for capturing images
while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Unable to read from the camera.")
        break
    
    # Convert image to grayscale
    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = detector.detectMultiScale(converted_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        count += 1
        face_img = converted_image[y:y + h, x:x + w]
        
        # Save image in a separate thread
        threading.Thread(target=save_image, args=(face_img, face_id, count)).start()
        
        cv2.imshow('image', img)
    
    k = cv2.waitKey(100) & 0xff
    if k == 27 or count >= 500:  # Exit if 'ESC' is pressed or 50 samples are collected
        break

print("Samples taken, now closing the program...")
cam.release()
cv2.destroyAllWindows()
