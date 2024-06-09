import requests
import pyttsx3
import speech_recognition as sr
import datetime
import os
import subprocess
import cv2
import wikipedia
import webbrowser
import pywhatkit as kit
import smtplib
from email.message import EmailMessage
import sys
import google.api_core.client_options
from googleapiclient.discovery import build
import google.generativeai as genai
import spacy
import numpy as np
import base64
import urllib.request
import time
import pymongo
import pyautogui
from newsapi import NewsApiClient
import pytesseract
from google.api_core.exceptions import InternalServerError
import PyPDF2
from bs4 import BeautifulSoup
import shed

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rosha\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Replace with your actual values
GMAIL_EMAIL = "YOUR MAIL"
GMAIL_PASSWORD = "YOUR PASSWORD"
GEMINI_API_KEY = "YOUR API KEY"
NEWS_API_KEY = "f61c86e7a3a84910ac561447c2b2990c"
db= client["jarvis_db"]
collection=db["settings"]
result = collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])
voice = result.get('volume')

def set_volume(voice):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(voice / 100.0, None)
# Function to get the latest settings from the database
def get_latest_settings_from_database():
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Access the database
        db = client["jarvis_db"]
        # Access the collection
        collection = db["settings"]
        # Find the latest document by sorting in descending order of _id and limiting to 1
        result = collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])
        # Access the 'voice' field from the result
        voice = result.get('voice')
        # Perform some logic based on the value of 'voice'
        if voice == 'Select' or voice == 'JARVIS':
            return 0
        else:
            return 1
    except pymongo.errors.PyMongoError as e:
        print("Error fetching latest settings from database:", e)
        return None
    finally:
        # Close the MongoDB connection
        client.close()

# Function to fetch the latest news
def fetch_news():
    try:
        speak("Please wait sir, fetching the latest news for India")
        # Using NewsAPI
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        top_headlines = newsapi.get_top_headlines(language='en', country='in')
        articles = top_headlines['articles']
        for article in articles[:5]:  # Fetch top 5 news articles
            speak(article['title'])
            print(article['title'])
    except Exception as e:
        speak("Sorry, I couldn't fetch the news.")
        print("Error fetching news:", e)

voice = get_latest_settings_from_database()

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[voice].id)
engine.setProperty('rate',175)
# Speaking function
def speak(audio):
    try:
        engine.say(audio)
        print(audio)
        engine.runAndWait()
    except Exception as e:
        print("Error speaking:", e)

# Open camera function
def open_camera():
    try:
        speak("Opening camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Could not open webcam")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                speak("Failed to capture image")
                break
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        speak("Error opening camera.")
        print("Error opening camera:", e)

# Listening function
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            speak("Listening timed out, please try again...")
            return "none"
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        return query
    except sr.UnknownValueError:
        speak("I didn't understand what you said, please say that again...")
        return "none"
    except sr.RequestError as e:
        speak(f"Could not request results; {e}")
        return "none"

# Wishing function
def wish():
    try:
        hour = datetime.datetime.now().hour
        if hour >= 0 and hour < 12:
            speak("Good Morning!")
        elif hour >= 12 and hour < 18:
            speak("Good Afternoon!")
        else:
            speak("Good Evening!")
        speak("How can I assist you today?")
    except Exception as e:
        print("Error in wish function:", e)

# Fetch IP address function
def get_ip_address():
    try:
        ip = requests.get('http://api.ipify.org').text
        speak(f"Your IP address is {ip}")
    except requests.RequestException as e:
        speak(f"Could not get IP address; {e}")

# Function to fetch email address from MongoDB based on name
def get_email_from_database(name):
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Access the database
        db = client["jarvis_db"]
        # Access the collection
        collection = db["entries"]
        # Find the document with the provided name
        query = {"name": name}
        result = collection.find_one(query)
        if result:
            email_address = result.get("email")
            return email_address
        else:
            return None
    except pymongo.errors.PyMongoError as e:
        print("Error fetching email from database:", e)
        return None
    finally:
        # Close the MongoDB connection
        client.close()

# Send email function
def sendEmail(to, content):
    try:
        to_email = get_email_from_database(to)
        if to_email:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            email_address = GMAIL_EMAIL  # Replace with your email address
            email_password = GMAIL_PASSWORD  # Replace with your email password
            server.login(email_address, email_password)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = 'Subject'
            msg['From'] = email_address
            msg['To'] = to_email
            server.send_message(msg)
            server.close()
            speak("Email has been sent!")
        else:
            speak("Email address not found in the database.")
    except Exception as e:
        print("Error sending email:", e)
        speak("I am not able to send the email at the moment.")

# Encode image to base64
def encode_image_to_base64(image):
    try:
        _, buffer = cv2.imencode('.jpg', image)
        encoded_string = base64.b64encode(buffer).decode("utf-8")
        return encoded_string
    except Exception as e:
        print("Error encoding image:", e)
        return None

# Function to read PDF
def pdf_reader():
    try:
        speak("Tell me the name of the PDF.")
        x = takecommand().lower()
        book = open(f"{x}.pdf", 'rb')
        pdfReader = PyPDF2.PdfReader(book)
        pages = len(pdfReader.pages)
        speak(f"Total number of pages in this book: {pages}")
        speak("Sir, please enter the page number I have to read.")
        pg = int(input("Please enter the page number: "))
        page = pdfReader.pages[pg-1]
        text = page.extract_text()
        speak(text)
        speak("Do you want to summarize the page?")
        x = takecommand().lower()
        if "yes" in x:
            genai.configure(api_key=GEMINI_API_KEY)  # Replace with your API key
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config
            )
            nlp = spacy.load("en_core_web_sm")
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(text)
            speak(response.text.replace("*"," "))
    except Exception as e:
        print("Error reading PDF:", e)
        speak("Sorry, I couldn't read the PDF.")

# Capture image from mobile camera
def capture_image_from_camera(url):
    try:
        while True:
            img_arr = np.array(bytearray(urllib.request.urlopen(url).read()), dtype=np.uint8)
            img = cv2.imdecode(img_arr, -1)
            cv2.imshow('IPWebcam', img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                return img
    except Exception as e:
        print("Error capturing image from camera:", e)
        return None

# Generate content using Gemini API
def generate_content_gemini(prompt):
    try:
        client_options = google.api_core.client_options.ClientOptions(api_key=GEMINI_API_KEY)
        client = build('gemini', 'v1beta', client_options=client_options)
        body = {'input_text': prompt}
        response = client.generate(body=body).execute()
        return response['output_text']
    except Exception as e:
        print("Error generating content using Gemini:", e)
        return None

def set_reminders():
    speak("Sir, schedule your events. For example, 'set reminder to 6:00 AM'")
    while True:
        reminder_time = input("Set reminder to: ").strip()
        if reminder_time.lower() == 'exit':
            break
        else:
            set_alarm(reminder_time)
def set_alarm(time_str):
    try:
        alarm_time = time.strptime(time_str, "%I:%M %p")
        alarm_timestamp = time.mktime(alarm_time)
        current_time = time.time()
        if alarm_timestamp > current_time:
            delay = alarm_timestamp - current_time
            shed.scheduler.enter(delay, 1, ring_alarm)
            print(f"Alarm set for {time_str}")
            speak(f"Alarm set for {time_str}")
        else:
            print("Please provide a future time for the alarm.")
            speak("Please provide a future time for the alarm.")
    except ValueError:
        print("Invalid time format. Please provide time in '6:00 AM' format.")
        speak("Invalid time format. Please provide time in '6:00 AM' format.")
def ring_alarm():
    print("Alarm ringing!")
    speak("Alarm ringing!")

def face_lock():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('traines/trainer.yml')
        cascadePath = 'haarcascade_frontalface_default.xml'
        faceCascade = cv2.CascadeClassifier(cascadePath)
        names = ['', 'avi', 'roshan']

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            speak("Error: Unable to open camera.")
            return False

        cam.set(3, 640)
        cam.set(4, 480)
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)

        while True:
            ret, img = cam.read()
            if not ret:
                speak("Error: Unable to read frame from camera.")
                break

            converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                converted_image,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH))
            )

            for (x, y, w, h) in faces:
                _id, accuracy = recognizer.predict(converted_image[y:y + h, x:x + w])

                if accuracy > 50:
                    accuracy = round(100 - accuracy)
                    name = names[2]
                    cam.release()
                    cv2.destroyAllWindows()
                    return True
                else:
                    accuracy = round(100 - accuracy)
                    print(f"Unrecognized face with accuracy: {accuracy}%")

            cv2.imshow('Face Lock', img)

            if cv2.waitKey(10) & 0xff == 27:
                break

        cam.release()
        cv2.destroyAllWindows()
        return False
    except cv2.error as e:
        speak("There was an error with the OpenCV library.")
        print("OpenCV error:", e)
        return False
    except Exception as e:
        speak("An unexpected error occurred during face lock.")
        print("Unexpected error:", e)
        return False

# Main task function
def task():
    if face_lock():
        wish()
        while True:
            query = takecommand().lower()
            if query == "none":
                continue

            if "open notepad" in query:
                try:
                    os.startfile("C:\\Windows\\notepad.exe")
                except Exception as e:
                    speak("Could not open Notepad.")
                    print("Error opening Notepad:", e)
            
            elif "open command prompt" in query:
                try:
                    os.system("start cmd")
                except Exception as e:
                    speak("Could not open Command Prompt.")
                    print("Error opening Command Prompt:", e)
            
            elif "open setting" in query:
                try:
                    speak("Opening setting panel")
                    command = "python -m streamlit run test.py"
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        speak(f"Failed to run Streamlit app: {result.stderr}")
                    else:
                        speak("Streamlit app started successfully. Please close the Streamlit window to continue.")
                except Exception as e:
                    speak(f"An error occurred: {e}")
                    print("Error opening setting:", e)
            
            elif "open camera" in query:
                open_camera()

            elif "ip address" in query:
                get_ip_address()
            
            elif "wikipedia" in query:
                try:
                    speak("Searching Wikipedia...")
                    query = query.replace("wikipedia", "")
                    results = wikipedia.summary(query, sentences=2)
                    speak("According to Wikipedia")
                    speak(results)
                    print(results)
                except wikipedia.exceptions.DisambiguationError:
                    speak("There are multiple results for this topic. Please be more specific.")
                except wikipedia.exceptions.PageError:
                    speak("No page found for this topic.")
                except Exception as e:
                    speak("An error occurred while searching Wikipedia.")
                    print("Error searching Wikipedia:", e)
            
            elif "open youtube" in query:
                try:
                    webbrowser.open("https://youtube.com")
                except Exception as e:
                    speak("Could not open YouTube.")
                    print("Error opening YouTube:", e)

            elif "open facebook" in query:
                try:
                    webbrowser.open("https://www.facebook.com")
                except Exception as e:
                    speak("Could not open Facebook.")
                    print("Error opening Facebook:", e)
            
            elif "open google" in query:
                try:
                    speak("What should I search on Google?")
                    cm = takecommand().lower()
                    webbrowser.open(f"https://www.google.com/search?q={cm}")
                except Exception as e:
                    speak("Could not perform Google search.")
                    print("Error performing Google search:", e)
            
            elif "send message" in query:
                try:
                    speak("What is the message?")
                    message = takecommand().lower()
                    kit.sendwhatmsg("PHONE NUMBER", message, 2, 25)
                    speak("Message sent successfully")
                except Exception as e:
                    print(e)
                    speak("Sorry, I was not able to send the message.")
            
            elif "play song on youtube" in query:
                try:
                    speak("Please tell me the song name")
                    song_name = takecommand()
                    kit.playonyt(song_name)
                except Exception as e:
                    speak("Could not play the song on YouTube.")
                    print("Error playing song on YouTube:", e)
            
            elif "send email" in query:
                try:
                    speak("What is the message?")
                    content = takecommand().lower()
                    speak("To whom are we sending the email?")
                    to = takecommand().lower()
                    sendEmail(to, content)
                except Exception as e:
                    print(e)
                    speak("Sorry, I am not able to send the email.")
            
            elif "close notepad" in query:
                try:
                    os.system("taskkill /f /im notepad.exe")
                    speak("Notepad closed")
                except Exception as e:
                    speak("Could not close Notepad.")
                    print("Error closing Notepad:", e)
            
            elif "shutdown" in query:
                try:
                    speak("Shutting down the computer")
                    os.system("shutdown /s /t 1")
                except Exception as e:
                    speak("Could not shut down the computer.")
                    print("Error shutting down the computer:", e)
            
            elif "restart" in query:
                try:
                    speak("Restarting the computer")
                    os.system("shutdown /r /t 1")
                except Exception as e:
                    speak("Could not restart the computer.")
                    print("Error restarting the computer:", e)
            
            elif "log off" in query:
                try:
                    speak("Logging off")
                    os.system("shutdown /l")
                except Exception as e:
                    speak("Could not log off.")
                    print("Error logging off:", e)
            
            elif "take screenshot" in query or "take a screenshot" in query:
                try:
                    speak("Please tell me the name for this screenshot file.")
                    name = takecommand().lower()
                    speak("Please hold the screen for a few seconds, I am taking the screenshot.")
                    time.sleep(3)
                    img = pyautogui.screenshot()
                    img.save(f"{name}.png")
                    speak("I am done, the screenshot is saved in our main folder.")
                except Exception as e:
                    speak("Could not take screenshot.")
                    print("Error taking screenshot:", e)
            elif "get text from image" in query:
                def capture_and_process():
                    print("Starting camera...")
                    camera = cv2.VideoCapture(0)

                    if not camera.isOpened():
                        speak("Error: Camera could not be opened.")
                        return

                    ret, frame = camera.read()
                    if not ret:
                        speak("Error: Unable to capture image from camera.")
                        camera.release()
                        return

                    print("Image captured from camera.")

        # Convert image to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use pytesseract to extract text
                    extracted_text = pytesseract.image_to_string(gray)
        
                    speak("Extracted Text:")
                    speak(extracted_text)

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
                    speak("Do you want to summerize the text")
                    x = takecommand().lower()
                    if "yes" in x:
                        genai.configure(api_key="YOUR API KEY ")

                        generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

                        model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

                        nlp = spacy.load("en_core_web_sm")
                        chat_session = model.start_chat(history=[])

                        response = chat_session.send_message(extracted_text)
                        speak(response.text.replace("*"," "))
                    else:
                        speak(extracted_text)



        
                    


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
                main()
    


            elif "no thanks" in query:
                speak("Have a good day!")
                sys.exit()
            elif 'switch the window' in query:
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.keyUp("alt")
            elif "tell me news" in query:
                speak("please wait sir,fetching the latest news")
                fetch_news()
            elif "where am i" in query or "where are we" in query:
                speak("Wait, let me check.")
                try:
                    ipAdd = requests.get("https://api.ipify.org").text
                    print(ipAdd)
                    url = f'https://get.geojs.io/v1/ip/geo/{ipAdd}.json'
                    geo_requests = requests.get(url)
                    geo_data = geo_requests.json()
                    city = geo_data.get('city')
                    country = geo_data.get('country')
                    if city and country:
                        speak(f"I am not sure, but I think we are in {city} city of {country} country.")
                    else:
                        speak("Sorry, I couldn't determine our location.")
                except Exception as e:
                    print(f"An error occurred while retrieving location data: {e}")
                    speak("Sorry, due to a network issue, I am not able to find where we are.")
            elif "read pdf" in query.lower():
                pdf_reader()
            elif "you can sleep" in query or "sleep now" in query:
                speak("okay sir, i am going to sleep you can call me anytime.")
                break
            elif "hide all files" in query or "hide this folder" in query or "visible for everyone" in query:
                speak("sir please tell me you want to hide this folder or make it visible ")
                condition = takecommand().lower()
                if "hide" in condition:
                    os.system("attrib +h /s /d")
                    speak("sir, all the files in this folder are now hidden")
                elif "visible" in condition:
                    os.system("attrib -h /s /d")
                    speak("sir, all the files in this folder are now visible to everyone.")
                elif "leave it" in condition or "leave for now" in condition:
                    speak("ok sir")
            elif "temperature" in query or "weather" in query:
                    try:
                        speak("For which city do you want to know the temperature?")
                        search = takecommand().lower()
                        command = f"weather of {search}"
                        url = f"https://www.google.com/search?q={command}"
        
                        r = requests.get(url)
                        r.raise_for_status()  # Raise an HTTPError for bad responses
        
                        data = BeautifulSoup(r.text, "html.parser")
                        temp = data.find("div", class_="BNeawe").text
        
                        speak(f"The current temperature in {search} is {temp}.")
                    except requests.exceptions.RequestException as e:
                        print("Error fetching weather data:", e)
                        speak("Sorry, I couldn't fetch the weather information due to a network issue.")
                    except Exception as e:
                        print("Error parsing weather data:", e)
                        speak("Sorry, I couldn't parse the weather information.")
            elif 'alarm' in query:
                speak("Sir, please tell me when to set the alarm. For example, 'set alarm to 6:00 AM'")
                time_str = input("Set alarm to: ").strip()
                set_alarm(time_str)
                

            elif 'set reminders' in query:
                set_reminders()

            elif "open mobile camera" in query:
                try:
                    camera_url = "YOUR CAMERA URL"
                    captured_image = capture_image_from_camera(camera_url)
                    if captured_image is not None:
                        encoded_image = encode_image_to_base64(captured_image)
                        prompt = {
                            "text": "Describe the image",
                            "image": encoded_image
                        }
                        genai.configure(api_key=GEMINI_API_KEY)  # Replace with your API key
                        generation_config = {
                            "temperature": 1,
                            "top_p": 0.95,
                            "top_k": 64,
                            "max_output_tokens": 8192,
                            "response_mime_type": "text/plain",
                        }
                        model = genai.GenerativeModel(
                            model_name="gemini-1.5-flash",
                            generation_config=generation_config
                        )
                        nlp = spacy.load("en_core_web_sm")
                        chat_session = model.start_chat(history=[])
                        response = chat_session.send_message(prompt)
                        speak(response.text)
                    else:
                        speak("Could not capture image from mobile camera.")
                except Exception as e:
                    speak("Error opening mobile camera.")
                    print("Error opening mobile camera:", e)
            
            else:
                genai.configure(api_key="YOUR API KEY")

                generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

                model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

                nlp = spacy.load("en_core_web_sm")
                chat_session = model.start_chat(history=[])

                response = chat_session.send_message(query)
                speak(response.text.replace("*"," "))

# To start the assistant

if __name__ == "__main__":
    while True:
        permission = takecommand().lower()
        db = client["jarvis_db"]

        # Access the collection
        collection = db["settings"]

        # Find the latest document by sorting in descending order of _id and limiting to 1
        result = collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])
        
        # Access the 'voice' field from the result
        voice = result.get('wake_word')
        if voice.lower() in permission:
            task()
        
        elif "goodbye" in permission:
            sys.exit()
        # Perform some logic based on the value of 'voice'