import unittest
import requests
import os

CATALOGUE_URL = "http://localhost:5001"
IDENTIFY_URL = "http://localhost:5002"
TEST_DIR = "wavs"  # Directory containing test audio files

class TestShamzamIntegration(unittest.TestCase):

    def test_1_add_track(self):
        """Test adding a song to the catalogue."""
        data = {
            "title": "Don't Look Back In Anger",
            "artist": "Oasis",
            "filename": "dont_look_back_in_anger.wav"
        }
        response = requests.post(f"{CATALOGUE_URL}/tracks", json=data)
        self.assertEqual(response.status_code, 201, "❌ Failed to add track to catalogue.")
        print("✅ Track added successfully!")

    def test_2_list_tracks(self):
        """Test listing tracks in the catalogue."""
        response = requests.get(f"{CATALOGUE_URL}/tracks")
        self.assertEqual(response.status_code, 200, "❌ Failed to retrieve track list.")
        tracks = response.json()
        self.assertTrue(isinstance(tracks, list))
        print(f"📜 Tracks found in catalogue: {tracks}")

    def test_3_identify_existing_track(self):
        """Test identifying a song that exists in the catalogue."""
        test_file = os.path.join(TEST_DIR, "~Don't Look Back In Anger.wav")

        if not os.path.exists(test_file):
            self.fail(f"❌ Test file not found: {test_file}")

        with open(test_file, "rb") as file:
            files = {"audio": file}
            response = requests.post(f"{IDENTIFY_URL}/identify", files=files)

        self.assertEqual(response.status_code, 200, "❌ Failed to identify existing track.")
        json_data = response.json()
        self.assertIn("file_url", json_data, "❌ Track found, but no file URL returned.")
        print(f"🎵 Found in catalogue: {json_data['file_url']}")

    def test_4_identify_missing_track(self):
        """Test identifying a song that does NOT exist in the catalogue."""
        test_file = os.path.join(TEST_DIR, "~Davos.wav")  # Speech file, not a song

        if not os.path.exists(test_file):
            self.fail(f"❌ Test file not found: {test_file}")

        with open(test_file, "rb") as file:
            files = {"audio": file}
            response = requests.post(f"{IDENTIFY_URL}/identify", files=files)

        self.assertEqual(response.status_code, 404, "❌ Expected a 404 for missing track, but got a different status.")
        json_data = response.json()
        self.assertIn("error", json_data, "❌ Missing track should return an error message.")
        print("🚫 Song not found in catalogue.")

if __name__ == "__main__":
    unittest.main()
