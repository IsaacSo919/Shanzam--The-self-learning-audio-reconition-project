import unittest
import requests

class TestShamzamIntegration(unittest.TestCase):
    def test_add_track(self):
        """Test adding a song to the catalogue."""
        data = {"title": "Test Song", "artist": "Test Artist", "filename": "test.wav"}
        response = requests.post("http://localhost:5001/tracks", json=data)
        self.assertEqual(response.status_code, 201)

    def test_identify_song_in_catalogue(self):
        """Test identifying a song that exists in the catalogue."""
        files = {"audio": open("Blinding_Lights.wav", "rb")}
        response = requests.post("http://localhost:5002/identify", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("file_url", response.json())

    def test_identify_song_not_in_catalogue(self):
        """Test identifying a song that is NOT in the catalogue."""
        files = {"audio": open("Davos.wav", "rb")}  # Davos speech, not in catalogue
        response = requests.post("http://localhost:5002/identify", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

if __name__ == "__main__":
    unittest.main()
