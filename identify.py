import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load API key from environment variable
AUDD_API_KEY = os.environ.get("AUDD_API_KEY")

@app.route("/identify", methods=["POST"])
def identify_song():
    # Check if a file was uploaded
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]

    # Prepare request to AudD.io
    files = {"file": (file.filename, file.stream, "audio/wav")}
    data = {"api_token": AUDD_API_KEY, "return": "apple_music,spotify"}

    # Send request to AudD.io API
    response = requests.post("https://api.audd.io/", files=files, data=data)

    if response.status_code == 200:
        return response.json(), 200
    else:
        return jsonify({"error": "Failed to recognize song", "details": response.text}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=5002)
