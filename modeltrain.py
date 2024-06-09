import cv2
import numpy as np
from PIL import Image
import os

# Define the path to the samples directory and the haarcascade file
path = 'Samples'
haarcascade_path = "haarcascade_frontalface_default.xml"

# Check for the correct method to create the LBPHFaceRecognizer
if hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
else:
    recognizer = cv2.face.createLBPHFaceRecognizer()

detector = cv2.CascadeClassifier(haarcascade_path)

def Image_And_Labels(path):
    # Get the paths of all files in the samples directory
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        # Convert image to grayscale
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')
        
        # Extract the ID from the filename
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        
        # Detect faces in the image
        faces = detector.detectMultiScale(img_arr)
        
        # Extract each face and its corresponding ID
        for (x, y, w, h) in faces:
            faceSamples.append(img_arr[y:y+h, x:x+w])
            ids.append(id)

    return faceSamples, ids

# Print status message
print("Training faces. This may take a few seconds. Please wait...")

# Get the faces and IDs
faces, ids = Image_And_Labels(path)

# Train the recognizer on the faces and IDs
recognizer.train(faces, np.array(ids))

# Ensure the "traines" directory exists
if not os.path.exists('traines'):
    os.makedirs('traines')

# Save the trained model to a file
recognizer.write("traines/trainer.yml")

# Print completion message
print("Model trained. You can now recognize faces.")
