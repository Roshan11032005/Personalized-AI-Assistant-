import tkinter as tk
from tkinter import font
import subprocess
import os
import signal

# Function to start the jarvis.py script
def start_jarvis():
    global jarvis_process
    jarvis_process = subprocess.Popen(['python', 'jarvis.py'])
    start_button.config(state="disabled")  # Disable the start button
    start_label.config(text="Jarvis started")  # Update the label text

# Function to stop the jarvis.py script and close the Tkinter application
def stop_jarvis():
    if jarvis_process:
        os.kill(jarvis_process.pid, signal.SIGTERM)
    root.destroy()

# Custom Button class
class CustomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief=tk.FLAT,    # Remove button relief
            bd=0,              # Remove border
            highlightthickness=0,  # Remove highlight
            padx=10,           # Add horizontal padding
            pady=5,            # Add vertical padding
            font=("Arial", 12),  # Set font
            foreground="white",  # Text color
            background="orange", # Background color
        )
        # Bind events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        self.config(background="lightblue")  # Change color on hover

    def on_leave(self, event):
        self.config(background="orange")  # Restore original color

# Create the main window
root = tk.Tk()
root.title("Jarvis Controller")

# Set window size and make it not resizable
root.geometry("800x600")
root.resizable(False, False)

# Define custom font
button_font = font.Font(family="Helvetica", size=14, weight="bold")

# Define custom colors
stop_color = "#f44336"   # Red color

# Define custom button styles
button_style = {
    "foreground": "white",       # Text color
    "font": button_font,         # Font style
    "activeforeground": "white", # Text color on hover
    "relief": "flat",            # Flat border style
    "highlightthickness": 0,     # Remove focus border
    "width": 15                  # Width of the button
}

# Add a custom button to start Jarvis
start_button = CustomButton(root, text="Start Jarvis", command=start_jarvis, **button_style)
start_button.pack(pady=20)

# Add a label to indicate Jarvis has started
start_label = tk.Label(root, text="", font=("Helvetica", 14))
start_label.pack()

# Add a button to stop Jarvis and close the application
stop_button = tk.Button(root, text="End", command=stop_jarvis, bg=stop_color, **button_style)
stop_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
