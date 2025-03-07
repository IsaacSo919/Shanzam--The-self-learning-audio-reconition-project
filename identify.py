import os
import requests
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
AUDD_API_KEY = os.environ.get("AUDD_API_KEY")

def check_in_catalogue(title, artist):
    """Check if a song exists in the local music catalogue."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("SELECT filename FROM tracks WHERE title=? AND artist=?", (title, artist))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

@app.route("/identify", methods=["POST"])
def identify_song():
    """Identify a song fragment and check if it exists in the catalogue."""
    if "audio" not in request.files:
        print("\n❌ No audio file received.\n")
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    print(f"\n📥 Received file: {file.filename}")

    files = {"file": (file.filename, file.stream, "audio/wav")}
    data = {"api_token": AUDD_API_KEY, "return": "apple_music,spotify"}

    print("📡 Sending request to AudD.io...")
    response = requests.post("https://api.audd.io/", files=files, data=data)

    if response.status_code != 200:
        print(f"❌ AudD.io failed: {response.text}\n")
        return jsonify({"error": "Failed to recognize song"}), 500

    result = response.json().get("result")
    if not result:
        print("❌ No song recognized.\n")
        return jsonify({"error": "Song not recognized"}), 404

    title, artist = result.get("title", "Unknown"), result.get("artist", "Unknown")
    spotify = result.get("spotify", {}).get("link", "N/A")
    apple_music = result.get("apple_music", {}).get("link", "N/A")

    print("\n✅ **Song Identified Successfully**")
    print(f"🎵 Title  : {title}")
    print(f"🎤 Artist : {artist}")
    print(f"🔗 Spotify: {spotify}")
    print(f"🍏 Apple Music: {apple_music}")

    # Check if song is in the local catalogue
    local_file = check_in_catalogue(title, artist)
    if local_file:
        print(f"🎶 Available in catalogue: {local_file}\n")
        return jsonify({
            "title": title,
            "artist": artist,
            "file_url": f"http://localhost:5001/files/{local_file}"
        }), 200
    else:
        print("🚫 Song not found in local catalogue.\n")
        return jsonify({
            "title": title,
            "artist": artist,
            "message": "This song is not available in the local catalogue."
        }), 200

if __name__ == "__main__":
    app.run(host="localhost", port=5002)
