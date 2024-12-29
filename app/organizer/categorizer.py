from transformers import pipeline
from app.cleaner.cleaner import TextCleaner

class ContentCategorizer:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def categorize(self, text, candidate_labels, threshold=0.3, multi_label=True):
        """
        Clean and categorize text using multi-label zero-shot classification.
        """
        # Clean the text
        cleaned_text = self.cleaner.clean_text(text)

        # Handle empty text
        if not cleaned_text.strip():
            return [] 

        # Perform classification
        result = self.classifier(cleaned_text, candidate_labels, multi_label=multi_label)

        # Return all labels with scores above the threshold
        labels = [
            label for label, score in zip(result["labels"], result["scores"]) if score >= threshold
        ]
        return labels
