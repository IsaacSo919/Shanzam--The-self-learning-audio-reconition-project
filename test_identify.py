import requests
import unittest

class TestIdentifyService(unittest.TestCase):
    def test_identify_song(self):
        files = {"audio": open("Blinding_Lights.wav", "rb")}
        response = requests.post("http://localhost:5002/identify", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.json())

if __name__ == "__main__":
    unittest.main()
