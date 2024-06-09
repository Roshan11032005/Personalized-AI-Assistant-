import streamlit as st
from PIL import Image
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Adjust the URI as needed
db = client.jarvis_db
settings_collection = db.settings
entries_collection = db.entries

# Title with centered alignment and background color
st.title("JARVIS Settings Panel")
st.markdown("<h1 style='text-align: center; color: white; background-color: #1E90FF;'>JARVIS Settings Panel</h1>", unsafe_allow_html=True)

# Header with centered alignment and background color
st.header('JARVIS - Concept to Easy Life')
st.markdown("<h2 style='text-align: center; color: black; background-color: #80ced6;'>JARVIS - Concept to Easy Life</h2>", unsafe_allow_html=True)

# Add a separator
st.markdown("---")

# Image with centered alignment
img = Image.open('jarvisimg.jpg')
st.image(img, caption='Personal Voice Assistant', use_column_width=True)

# Add some spacing
st.write("\n")

# Text with centered alignment
st.text("JARVIS - It's the future. It's just a life assistant which makes life easier.")
st.markdown("<p style='text-align: center;'>JARVIS - It's the future. It's just a life assistant which makes life easier.</p>", unsafe_allow_html=True)

# Add a separator
st.markdown("---")

# Text Input for Wake Word with centered alignment
wake_word = st.text_input("Enter Wake Word")
st.markdown("<p style='text-align: center;'>Enter Wake Word</p>", unsafe_allow_html=True)

# Selectbox for Voice Selection with centered alignment
voice = st.selectbox("SELECT VOICE", ['Select', 'JARVIS', 'EDITH'])
st.markdown("<p style='text-align: center;'>SELECT VOICE</p>", unsafe_allow_html=True)
volume = None
if voice != 'Select':
    st.write('Selected', voice, 'Voice')

    # Slider for Volume Level
    volume = st.slider("Volume Level", 25, 100)

# Add some spacing
st.write("\n")

# Main function for multiple name and email entries
def main():
    st.subheader("Multiple Name and Email List")

    num_entries = st.number_input(
        "How many entries do you want to add?",
        min_value=1,
        max_value=10,
        step=1
    )

    entries = []
    for i in range(num_entries):
        name = st.text_input(f"Name {i + 1}")
        email = st.text_input(f"Email {i + 1}")
        if name and email:  # Ensure both name and email are provided
            entries.append((name.lower(), email))

    if st.button('Save Entries'):
        entries_data = [{"name": entry[0], "email": entry[1]} for entry in entries]
        if entries_data:
            entries_collection.insert_many(entries_data)
            st.success('Entries saved successfully!')

    st.subheader("List of Entries")
    for i, entry in enumerate(entries):
        st.write(f"Entry {i + 1}: Name - {entry[0]}, Email - {entry[1]}")


main()

# Add a separator
st.markdown("---")

# Subheader for About Section with centered alignment and background color
st.subheader('About')
st.markdown("<h3 style='text-align: center; color: white; background-color: #1E90FF;'>About</h3>", unsafe_allow_html=True)

# Text for About Section with centered alignment
st.text(
    '''Welcome to the Jarvis Settings Panel! Customize your digital assistant experience 
with ease. Fine-tune voice recognition, adjust notifications, explore cool features. 
Let's optimize productivity together!'''
)
st.markdown("<p style='text-align: center;'>Welcome to the Jarvis Settings Panel! Customize your digital assistant experience with ease. Fine-tune voice recognition, adjust notifications, explore cool features. Let's optimize productivity together!</p>", unsafe_allow_html=True)

# Add some spacing
st.write("\n")

# Checkbox for Auto-Update with centered alignment
auto_update = st.checkbox('Auto-Update')
st.markdown("<p style='text-align: center;'>Auto-Update</p>", unsafe_allow_html=True)

# Add a separator
st.markdown("---")

# Subheader for Thank You Section with centered alignment and background color
st.subheader('Thank you for using JARVIS')
st.markdown("<h3 style='text-align: center; color: white; background-color: #1E90FF;'>Thank you for using JARVIS</h3>", unsafe_allow_html=True)

# Text Input for Feedback with centered alignment
feedback = st.text_input("Feedback")
st.markdown("<p style='text-align: center;'>Feedback</p>", unsafe_allow_html=True)

# Button to Save Settings to MongoDB
if st.button('Save Settings'):
    settings_data = {
        "wake_word": wake_word,
        "voice": voice,
        "volume": volume,
        "auto_update": auto_update,
        "feedback": feedback
    }
    settings_collection.insert_one(settings_data)
    st.success('Settings saved successfully!')

# Display all settings from MongoDB
st.subheader('All Settings')
settings = settings_collection.find()
for setting in settings:
    st.write(setting)

# Display all entries from MongoDB
st.subheader('All Entries')
all_entries = entries_collection.find()
for entry in all_entries:
    st.write(entry)