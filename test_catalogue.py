import unittest
import requests

class TestCatalogueService(unittest.TestCase):
    def test_add_track(self):
        data = {"title": "Test Song", "artist": "Test Artist", "filename": "test.wav"}
        response = requests.post("http://localhost:5001/tracks", json=data)
        self.assertEqual(response.status_code, 201)# 201 is the status code for created

    def test_list_tracks(self):
        response = requests.get("http://localhost:5001/tracks")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))

    def test_remove_track(self):
        response = requests.delete("http://localhost:5001/tracks/1")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
