import unittest
from run import create_app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_scrape(self):
        response = self.client.post("/scrape", json={"url": "http://example.com"})
        self.assertEqual(response.status_code, 202)

    def test_scrape_status(self):   
        response = self.client.get("/scrape_status/job_1")
        self.assertIn("status", response.json)

if __name__ == "__main__":
    unittest.main()