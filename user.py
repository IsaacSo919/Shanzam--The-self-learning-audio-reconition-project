import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame  # Used to play the audio

IDENTIFY_URL = "http://localhost:5002/identify"

def play_song(file_url):
    """Play the song using pygame."""
    try:
        print(f"🎵 Playing song from: {file_url}")

        # Download the song file from the server
        response = requests.get(file_url, stream=True)

        if response.status_code == 200:
            # Save the file temporarily
            temp_file = "temp_song.wav"
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # Initialize pygame and play the song
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            messagebox.showinfo("Playing", "🎵 Now playing the song. Close this box to stop.")
            pygame.mixer.music.stop()  # Stop when the message box is closed

        else:
            messagebox.showerror("Error", "❌ Could not download the song from the database.")

    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to play song: {str(e)}")

def select_file_and_identify():
    """Open file explorer to select an audio file and send it to the identification service."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(title="Select an Audio File",
                                           filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])

    if not file_path:
        print("❌ No file selected. Exiting...")
        return None

    print(f"📤 Sending file: {file_path}")

    # Open file safely using "with open" (prevents file locking issues)
    try:
        with open(file_path, "rb") as file:
            files = {"audio": file}
            response = requests.post(IDENTIFY_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            title = result.get("title", "Unknown Title")
            artist = result.get("artist", "Unknown Artist")
            file_url = result.get("file_url", None)  # Get song file URL if available
            print(file_url)
            print("\n✅ **Song Identified Successfully**")
            print(f"🎵 Title    : {title}")
            print(f"🎤 Artist   : {artist}")

            if file_url:
                print(f"🎶 Full Track Available: {file_url}")
                play_song(file_url)  # Play the song if available in the database
            else:
                print("🚫 The full track is NOT available in the database.")
                messagebox.showwarning("Song Not Found", "🚫 The full track is NOT available in the database.")

        else:
            print(f"❌ API Error: {response.json().get('error', 'Unknown error')}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to `identify.py` service.")

if __name__ == "__main__":
    pygame.init()  # Initialize pygame for playing audio
    select_file_and_identify()
