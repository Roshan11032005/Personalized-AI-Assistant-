import cv2
import pytesseract
import os

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rosha\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Function to capture image from camera and extract text
def capture_and_process():
    print("Starting camera...")
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Camera could not be opened.")
        return

    ret, frame = camera.read()
    if not ret:
        print("Error: Unable to capture image from camera.")
        camera.release()
        return

    print("Image captured from camera.")

    # Convert image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text
    extracted_text = pytesseract.image_to_string(gray)
    
    print("Extracted Text:")
    print(extracted_text)

    # Release the camera
    camera.release()
    cv2.destroyAllWindows()

# Function to load image from file and process it
def load_process_and_extract_text(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Load image
    image = cv2.imread(file_path)
    if image is None:
        print(f"Error: Failed to load the image from '{file_path}'.")
        return

    print(f"Image loaded from file: {file_path}")

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text
    extracted_text = pytesseract.image_to_string(gray)
    
    print("Extracted Text:")
    print(extracted_text)

# Main function
def main():
    choice = input("Do you want to (1) Capture from camera or (2) Load image from file? Enter 1 or 2: ")

    if choice == '1':
        capture_and_process()
    elif choice == '2':
        file_path = input("Enter the full path of the image file: ")
        load_process_and_extract_text(file_path)
    else:
        print("Invalid choice. Exiting.")
