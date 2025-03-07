import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import os

# API Endpoints
CATALOGUE_URL = "http://localhost:5001"
IDENTIFY_URL = "http://localhost:5002/recognize"  


def fetch_tracks():
    """Fetch all tracks from the catalogue and update the UI list."""
    try:
        response = requests.get(f"{CATALOGUE_URL}/tracks")
        if response.status_code == 200:
            track_list.delete(0, tk.END)
            tracks = response.json()
            for track in tracks:
                track_list.insert(tk.END, f"{track['id']} - {track['title']} by {track['artist']}")
        else:
            messagebox.showerror("Error", "Failed to fetch tracks.")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Could not connect to the catalogue service.")

def select_file():
    """Open file explorer, select a track, and use /recognize to fetch details."""
    file_path = filedialog.askopenfilename(title="Select Full Song File",
                                           filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
    if not file_path:
        return  # User canceled file selection

    filename = os.path.basename(file_path)  # Extract filename
    filename_label.config(text=f"📂 Selected File: {filename}")

    # Send the file to /recognize for song details
    try:
        with open(file_path, "rb") as file:
            files = {"audio": file}
            response = requests.post(IDENTIFY_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            title = result.get("title", "Unknown Title")
            artist = result.get("artist", "Unknown Artist")

            # Display results in UI
            title_entry.delete(0, tk.END)
            title_entry.insert(0, title)

            artist_entry.delete(0, tk.END)
            artist_entry.insert(0, artist)

            messagebox.showinfo("Song Identified", f"✅ Song: {title}\n🎤 Artist: {artist}\n🔗 Spotify: {spotify_link}\n🍏 Apple Music: {apple_music_link}")

        else:
            messagebox.showerror("Error", "Failed to recognize song using identify.py.")

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Could not connect to recognize service.")


def add_track():
    """Add a track to the catalogue."""
    title = title_entry.get()
    artist = artist_entry.get()
    filename = filename_label.cget("text").replace("📂 Selected File: ", "")

    if not title or not artist or filename == "No file selected":
        messagebox.showwarning("Warning", "Please select a file and ensure details are filled.")
        return

    # Check if track already exists
    response = requests.get(f"{CATALOGUE_URL}/tracks")
    if response.status_code == 200:
        existing_tracks = response.json()
        for track in existing_tracks:
            if track["title"].lower() == title.lower() and track["artist"].lower() == artist.lower():
                messagebox.showwarning("Warning", f"⚠️ Track '{title}' by {artist} already exists in the database.")
                return

    # Add track to the catalogue
    data = {"title": title, "artist": artist, "filename": filename}
    response = requests.post(f"{CATALOGUE_URL}/tracks", json=data)

    if response.status_code == 201:
        messagebox.showinfo("Success", "✅ Track added successfully.")
        fetch_tracks()
    else:
        messagebox.showerror("Error", "Failed to add track.")

def delete_selected_track():
    """Delete the selected track from the catalogue."""
    try:
        selected = track_list.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a track to delete.")
            return

        track_id = track_list.get(selected[0]).split(" - ")[0]
        response = requests.delete(f"{CATALOGUE_URL}/tracks/{track_id}")

        if response.status_code == 200:
            messagebox.showinfo("Success", "✅ Track deleted successfully.")
            fetch_tracks()
        else:
            messagebox.showerror("Error", "Failed to delete track.")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Could not connect to the catalogue service.")

# Initialize Tkinter window
admin_root = tk.Tk()
admin_root.title("Admin Track Manager")
admin_root.geometry("600x500")

# Title Label
title_label = tk.Label(admin_root, text="🎵 Admin Track Manager", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Track Listbox
track_list = tk.Listbox(admin_root, width=60, height=15)
track_list.pack(pady=10)

# Select File Button
select_button = tk.Button(admin_root, text="📂 Select Track File", command=select_file, bg="#FFD700", fg="black", width=20)
select_button.pack(pady=5)

# File Display Label
filename_label = tk.Label(admin_root, text="No file selected", font=("Arial", 10))
filename_label.pack()

# Input Fields
title_entry = tk.Entry(admin_root, width=40)
title_entry.pack(pady=5)

artist_entry = tk.Entry(admin_root, width=40)
artist_entry.pack(pady=5)

# Add & Delete Buttons
button_frame = tk.Frame(admin_root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="➕ Add Track", command=add_track, bg="#2196F3", fg="white", width=15)
add_button.grid(row=0, column=0, padx=5)

delete_button = tk.Button(button_frame, text="🗑 Delete Track", command=delete_selected_track, bg="#F44336", fg="white", width=15)
delete_button.grid(row=0, column=1, padx=5)

# Fetch tracks on startup
fetch_tracks()

# Run the Tkinter loop
admin_root.mainloop()
