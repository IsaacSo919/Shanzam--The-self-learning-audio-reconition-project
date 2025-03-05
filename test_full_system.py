import unittest
import requests

CATALOGUE_URL = "http://localhost:5001"
IDENTIFY_URL = "http://localhost:5002"

class TestShamzamIntegration(unittest.TestCase):

    def test_1_add_track(self):
        """Test adding a song to the catalogue."""
        data = {
            "title": "Don't Look Back In Anger",
            "artist": "Oasis",
            "filename": "dont_look_back_in_anger.wav"
        }
        response = requests.post(f"{CATALOGUE_URL}/tracks", json=data)
        self.assertEqual(response.status_code, 201)
        print("✅ Track added successfully!")

    def test_2_list_tracks(self):
        """Test listing tracks in the catalogue."""
        response = requests.get(f"{CATALOGUE_URL}/tracks")
        self.assertEqual(response.status_code, 200)
        tracks = response.json()
        self.assertTrue(isinstance(tracks, list))
        print(f"📜 Tracks found: {tracks}")

    def test_3_identify_existing_track(self):
        """Test identifying a song that exists in the catalogue."""
        files = {"audio": open("~Don't Look Back In Anger.wav", "rb")}
        response = requests.post(f"{IDENTIFY_URL}/identify", files=files)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("file_url", json_data)
        print(f"🎵 Found in catalogue: {json_data['file_url']}")

    def test_4_identify_missing_track(self):
        """Test identifying a song that does NOT exist in the catalogue."""
        files = {"audio": open("Davos.wav", "rb")}  # Speech file, not a song
        response = requests.post(f"{IDENTIFY_URL}/identify", files=files)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("message", json_data)
        print("🚫 Song not found in catalogue.")

if __name__ == "__main__":
    unittest.main()
