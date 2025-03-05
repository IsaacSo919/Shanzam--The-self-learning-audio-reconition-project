import os
import requests
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

AUDD_KEY = os.environ.get("AUDD_KEY")  # Ensure API key is set

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
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    files = {"file": (file.filename, file.stream, "audio/wav")}
    data = {"api_token": AUDD_KEY, "return": "apple_music,spotify"}

    response = requests.post("https://api.audd.io/", files=files, data=data)

    if response.status_code != 200:
        return jsonify({"error": "Failed to recognize song"}), 500

    result = response.json().get("result")

    if not result:
        return jsonify({"error": "Song not recognized"}), 404

    title, artist = result["title"], result["artist"]

    # Check if the track is in our catalogue
    local_file = check_in_catalogue(title, artist)

    if local_file:
        return jsonify({
            "title": title,
            "artist": artist,
            "file_url": f"http://localhost:5001/files/{local_file}"
        }), 200
    else:
        return jsonify({
            "title": title,
            "artist": artist,
            "message": "This song is not available in the local catalogue."
        }), 200

if __name__ == "__main__":
    app.run(host="localhost", port=5002)
