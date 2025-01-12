import unittest
from app.cleaner.cleaner import TextCleaner


class TestTextCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = TextCleaner()

    def test_clean_html(self):
        text = "<p>This is a <b>test</b>!</p>"
        cleaned = self.cleaner.clean_text(text)
        self.assertEqual(cleaned, "This is a test!")

    def test_remove_urls(self):
        text = "Visit for more info."
        cleaned = self.cleaner.clean_text(text)
        self.assertEqual(cleaned, "Visit for more info.")

    def test_remove_extra_spaces(self):
        text = "  This    is   spaced out.   "
        cleaned = self.cleaner.clean_text(text)
        self.assertEqual(cleaned, "This is spaced out.")


if __name__ == "__main__":
    unittest.main()
