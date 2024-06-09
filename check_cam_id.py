import cv2

def list_available_cameras():
    available_cameras = []
    for index in range(10):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

def list_available_cameras_dshow():
    available_cameras = []
    for index in range(10):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
    return available_cameras

print("Checking cameras with default backend...")
available_cameras_default = list_available_cameras()
print("Available camera IDs with default backend:", available_cameras_default)

print("Checking cameras with DirectShow backend...")
available_cameras_dshow = list_available_cameras_dshow()
print("Available camera IDs with DirectShow backend:", available_cameras_dshow)

# Use the appropriate list based on what is found
available_cameras = available_cameras_default if available_cameras_default else available_cameras_dshow
print("Available camera IDs:", available_cameras)
