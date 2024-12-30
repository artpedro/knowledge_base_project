from transformers import pipeline

class ContentCategorizer:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def categorize(self, text, candidate_labels, threshold=0.3, multi_label=True):
        """
        Clean and categorize text using multi-label zero-shot classification.
        """


        # Perform classification
        result = self.classifier(text, candidate_labels, multi_label=multi_label)

        # Return all labels with scores above the threshold
        labels = [
            label for label, score in zip(result["labels"], result["scores"]) if score >= threshold
        ]
        return labels
