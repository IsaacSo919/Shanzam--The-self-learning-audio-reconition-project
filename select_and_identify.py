import requests
import tkinter as tk
from tkinter import filedialog

IDENTIFY_URL = "http://localhost:5002/identify"

def select_file_and_identify():
    """Open file explorer to select an audio file and send it to the identification service."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(title="Select an Audio File",
                                           filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])

    if not file_path:
        print("❌ No file selected. Exiting...")
        return

    print(f"📤 Sending file: {file_path}")

    files = {"audio": open(file_path, "rb")}
    response = requests.post(IDENTIFY_URL, files=files)

    if response.status_code == 200:
        result = response.json()
        print("\n✅ **Song Identified Successfully**")
        print(f"🎵 Title  : {result.get('title', 'Unknown')}")
        print(f"🎤 Artist : {result.get('artist', 'Unknown')}")
        print(f"🔗 Spotify: {result.get('spotify', {}).get('link', 'N/A')}")
        print(f"🍏 Apple Music: {result.get('apple_music', {}).get('link', 'N/A')}\n")
    else:
        print(f"❌ Error: {response.json().get('error', 'Unknown error')}")

if __name__ == "__main__":
    select_file_and_identify()
