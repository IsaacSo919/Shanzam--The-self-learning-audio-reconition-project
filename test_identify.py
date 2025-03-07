import requests
import os
import unittest

IDENTIFY_URL = "http://localhost:5002/identify"
RECOGNIZE_URL = "http://localhost:5002/recognize"
TEST_DIR = "wavs"  # Folder where test audio files are stored
TEST_FILE = "~Blinding Lights.wav"  # Change this to test different files

class TestIdentifyAPI(unittest.TestCase):

    def setUp(self):
        """Prepare the full path to the test file."""
        self.file_path = os.path.join(TEST_DIR, TEST_FILE)
        if not os.path.exists(self.file_path):
            self.fail(f"❌ Error: Test file not found at {self.file_path}")

    def test_1_recognize_song(self):
        """Test if /recognize correctly identifies a song using AudD.io."""
        with open(self.file_path, "rb") as file:
            files = {"audio": file}
            response = requests.post(RECOGNIZE_URL, files=files)

        print("\n📡 Sending test audio to `/recognize`...")
        print(f"🔍 Response Status: {response.status_code}")

        self.assertEqual(response.status_code, 200, "❌ Failed to recognize song.")

        json_data = response.json()
        self.assertIn("title", json_data, "❌ Response missing 'title'.")
        self.assertIn("artist", json_data, "❌ Response missing 'artist'.")

        print("\n✅ **Test Passed: Song Identified Successfully**")
        print(f"📂 File      : {TEST_FILE}")
        print(f"🎵 Title    : {json_data.get('title', 'Unknown Title')}")
        print(f"🎤 Artist   : {json_data.get('artist', 'Unknown Artist')}")
    
    # def test_2_identify_existing_track(self):
    #     """Test if /identify correctly finds a song that exists in the catalogue."""
    #     with open(self.file_path, "rb") as file:
    #         files = {"audio": file}
    #         response = requests.post(IDENTIFY_URL, files=files)

    #     print("\n📡 Sending test audio to `/identify`...")
    #     print(f"🔍 Response Status: {response.status_code}")

    #     self.assertEqual(response.status_code, 200, "❌ Failed to identify existing track.")

    #     json_data = response.json()
    #     self.assertIn("file_url", json_data, "❌ Track found, but no file URL returned.")

    #     print(f"🎵 Found in catalogue: {json_data['file_url']}")

    # def test_3_identify_missing_track(self):
    #     """Test if /identify correctly reports a missing track in the database."""
    #     missing_file = os.path.join(TEST_DIR, "Unknown_Song.wav")

    #     if not os.path.exists(missing_file):
    #         self.fail(f"❌ Error: Test file not found at {missing_file}")

    #     with open(missing_file, "rb") as file:
    #         files = {"audio": file}
    #         response = requests.post(IDENTIFY_URL, files=files)

    #     print("\n📡 Sending test audio to `/identify` (expecting missing track)...")
    #     print(f"🔍 Response Status: {response.status_code}")

    #     self.assertEqual(response.status_code, 404, "❌ Expected a 404 for missing track.")
    #     json_data = response.json()
    #     self.assertIn("error", json_data, "❌ Missing track should return an error message.")

    #     print("🚫 Song not found in catalogue.")

if __name__ == "__main__":
    unittest.main()
