import os
import requests
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
AUDD_API_KEY = os.environ.get("AUDD_API_KEY")

if not AUDD_API_KEY:
    print("❌ ERROR: `AUDD_API_KEY` is not set. Please set the environment variable before running.")

DATABASE_FILE = "music_catalogue.db"

def recognize_song(file):
    """Send the audio file to AudD.io for recognition."""
    files = {"file": (file.filename, file.stream, "audio/wav")}
    data = {"api_token": AUDD_API_KEY, "return": "apple_music,spotify"}

    print("📡 Sending request to AudD.io for recognition...")
    response = requests.post("https://api.audd.io/", files=files, data=data)

    if response.status_code != 200:
        print(f"❌ AudD.io API Error: {response.text}")
        return None, "Failed to recognize song"

    result = response.json().get("result")

    if not result:
        print("❌ No song recognized.")
        return None, "Song not recognized"

    print(f"✅ Song Identified: {result.get('title', 'Unknown Title')} by {result.get('artist', 'Unknown Artist')}")
    return result, None  # Return the song details and no error

def check_in_catalogue(title, artist):
    """Check if a song exists in the local music catalogue."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT filename FROM tracks WHERE title=? AND artist=?", (title, artist))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
        return None

@app.route("/recognize", methods=["POST"])
def recognize():
    """Recognize a song using AudD.io but do not check the catalogue."""
    
    if "audio" not in request.files:
        print("❌ No audio file received.")
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    print(f"📥 Received file for recognition: {file.filename}")

    result, error = recognize_song(file)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "title": result.get("title", "Unknown Title"),
        "artist": result.get("artist", "Unknown Artist"),
        "spotify": result.get("spotify", {}).get("link", "N/A"),
        "apple_music": result.get("apple_music", {}).get("link", "N/A")
    }), 200

@app.route("/identify", methods=["POST"])
def identify():
    """Recognize a song and check if the full track exists in the catalogue."""
    
    if "audio" not in request.files:
        print("❌ No audio file received.")
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    print(f"📥 Received file for identification: {file.filename}")

    result, error = recognize_song(file)
    if error:
        return jsonify({"error": error}), 500

    title, artist = result.get("title", "Unknown Title"), result.get("artist", "Unknown Artist")
    spotify_link = result.get("spotify", {}).get("link", "N/A")
    apple_music_link = result.get("apple_music", {}).get("link", "N/A")

    print(f"🔍 Checking catalogue for: {title} by {artist}")
    local_file = check_in_catalogue(title, artist)

    if local_file:
        print(f"🎵 Track found in catalogue: {local_file}")
        return jsonify({
            "title": title,
            "artist": artist,
            "spotify": spotify_link,
            "apple_music": apple_music_link,
            "file_url": f"http://localhost:5001/files/{local_file}"
        }), 200
    else:
        print("🚫 The full track is NOT available in the database.")
        return jsonify({
            "title": title,
            "artist": artist,
            "spotify": spotify_link,
            "apple_music": apple_music_link,
            "error": "❌ The full track is NOT available in the database."
        }), 404

if __name__ == "__main__":
    app.run(host="localhost", port=5002)
