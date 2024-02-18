import unittest
import sys
from os.path import dirname, abspath, join

sys.path.insert(0, join(dirname(abspath(__file__)), ".."))

from app import app


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_track_visit(self):
        response = self.app.post("/track-visit", json={})
        self.assertEqual(response.status_code, 200)
        # Additional assertions can be made here


if __name__ == "__main__":
    unittest.main()
