import unittest
from app.organizer.categorizer import ContentCategorizer

class TestContentCategorizer(unittest.TestCase):
    def setUp(self):
        self.categorizer = ContentCategorizer()
        self.labels = [
            "Natural Language Processing",
            "Computer Vision",
            "Reinforcement Learning",
            "AI Ethics",
            "Generative AI",
            "Autonomous Systems",
        ]

    def test_single_label_classification(self):
        text = "Deep learning techniques are used for image and video real-time processing."
        category = self.categorizer.categorize(text, self.labels, threshold=0.3, multi_label=False)
        self.assertIn("Computer Vision",category)

    def test_multi_label_classification(self):
        text = "Reinforcement learning is used in robotics and autonomous vehicles."
        categories = self.categorizer.categorize(text, self.labels, threshold=0.3, multi_label=True)
        self.assertIn("Reinforcement Learning", categories)
        self.assertIn("Autonomous Systems", categories)

    def test_empty_text(self):
        text = ""
        categories = self.categorizer.categorize(text, self.labels, threshold=0.3, multi_label=True)
        self.assertEqual(categories, [])  # No categories for empty text

    def test_high_threshold(self):
        text = "Reinforcement learning is widely studied in robotics."
        categories = self.categorizer.categorize(text, self.labels, threshold=0.99, multi_label=True)
        self.assertEqual(categories, [])  # High threshold means no predictions

    def test_generative_ai_classification(self):
        text = "Generative AI models like GPT-3 create realistic text."
        categories = self.categorizer.categorize(text, self.labels, threshold=0.3, multi_label=True)
        self.assertIn("Generative AI", categories)

    def test_ai_ethics_classification(self):
        text = "AI Ethics focuses on bias and fairness in machine learning systems."
        categories = self.categorizer.categorize(text, self.labels, threshold=0.3, multi_label=True)
        self.assertIn("AI Ethics", categories)

if __name__ == "__main__":
    unittest.main()