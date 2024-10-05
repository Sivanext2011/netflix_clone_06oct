import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_movie(self):
        response = self.app.get('/movie/1')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
