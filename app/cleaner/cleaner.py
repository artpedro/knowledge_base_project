import re
import string


class TextCleaner:
    @staticmethod
    def clean_text(text):
        """
        Clean the scraped text by removing unwanted characters and formatting.
        """
        # Remove HTML tags
        text = re.sub(r"<.*?>", "", text)

        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()

        return text
