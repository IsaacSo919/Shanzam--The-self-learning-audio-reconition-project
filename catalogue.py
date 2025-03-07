from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

MUSIC_FOLDER = "wavs"  # Folder where music is stored

# Ensure the directory exists
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

def initialize_database():
    """Create the database and ensure the tracks table exists."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        filename TEXT UNIQUE
    )
    """)
    conn.commit()
    conn.close()

@app.route("/tracks", methods=["POST"])
def add_track():
    """Add a track to the database if it doesn't already exist."""
    data = request.json
    title, artist, filename = data.get("title"), data.get("artist"), data.get("filename")

    if not all([title, artist, filename]):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()

    # Check if the song already exists
    c.execute("SELECT * FROM tracks WHERE title=? AND artist=?", (title, artist))
    existing_track = c.fetchone()

    if existing_track:
        conn.close()
        return jsonify({"error": "Track already exists in the database."}), 409

    # Add new track
    c.execute("INSERT INTO tracks (title, artist, filename) VALUES (?, ?, ?)", (title, artist, filename))
    conn.commit()
    conn.close()

    return jsonify({"message": "Track added successfully"}), 201

@app.route("/tracks/<int:track_id>", methods=["DELETE"])
def delete_track(track_id):
    """Remove a track by ID."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()

    # Check if track exists before deleting
    c.execute("SELECT filename FROM tracks WHERE id=?", (track_id,))
    track = c.fetchone()

    if not track:
        conn.close()
        return jsonify({"error": "Track not found."}), 404

    filename = track[0]

    # Remove track from database
    c.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    conn.commit()
    conn.close()

    # Attempt to delete the file
    file_path = os.path.join(MUSIC_FOLDER, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)

    return jsonify({"message": "Track removed successfully"}), 200

@app.route("/tracks", methods=["DELETE"])
def remove_all_tracks():
    """Delete all tracks from the catalogue and remove all music files."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("DELETE FROM tracks")
    conn.commit()
    conn.close()

    # Delete all files in the music folder
    for file in os.listdir(MUSIC_FOLDER):
        file_path = os.path.join(MUSIC_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    return jsonify({"message": "All tracks deleted successfully"}), 200

@app.route("/tracks", methods=["GET"])
def list_tracks():
    """List all tracks in the catalogue."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("SELECT id, title, artist, filename FROM tracks")
    tracks = [{"id": row[0], "title": row[1], "artist": row[2], "filename": row[3]} for row in c.fetchall()]
    conn.close()

    return jsonify(tracks), 200

@app.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """Serve a music file if it exists in the music_files directory."""
    file_path = os.path.join(MUSIC_FOLDER, filename)
    print(file_path)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404

    return send_from_directory(MUSIC_FOLDER, filename)

if __name__ == "__main__":
    initialize_database()
    app.run(host="localhost", port=5001)
