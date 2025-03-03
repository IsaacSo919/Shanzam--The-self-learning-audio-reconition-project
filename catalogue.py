from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Create SQLite database if it doesn't exist
def init_db():
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        filename TEXT
    )
    """)
    conn.commit()
    conn.close()

@app.route("/tracks", methods=["POST"])
def add_track():
    """Add a track to the database."""
    data = request.json
    title, artist, filename = data.get("title"), data.get("artist"), data.get("filename")

    if not all([title, artist, filename]):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("INSERT INTO tracks (title, artist, filename) VALUES (?, ?, ?)", (title, artist, filename))
    conn.commit()
    conn.close()

    return jsonify({"message": "Track added successfully"}), 201

@app.route("/tracks/<int:track_id>", methods=["DELETE"])
def remove_track(track_id):
    """Remove a track by ID."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Track removed successfully"}), 200

@app.route("/tracks", methods=["GET"])
def list_tracks():
    """List all tracks in the catalogue."""
    conn = sqlite3.connect("music_catalogue.db")
    c = conn.cursor()
    c.execute("SELECT id, title, artist FROM tracks")
    tracks = [{"id": row[0], "title": row[1], "artist": row[2]} for row in c.fetchall()]
    conn.close()

    return jsonify(tracks), 200

if __name__ == "__main__":
    init_db()
    app.run(host="localhost", port=5001)
