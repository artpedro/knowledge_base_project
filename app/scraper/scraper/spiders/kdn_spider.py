import scrapy
from datetime import datetime


class KDnuggetsSpider(scrapy.Spider):
    name = "kdnuggets"
    allowed_domains = ["kdnuggets.com"]
    start_urls = ["https://www.kdnuggets.com/news/index.html"]

    title_selector = "div.li-has-thumb__content a b::text"  # Extracts the title
    author_selector = "div.author-link strong a::text"  # Extracts the author's name
    date_selector = "div.author-link::text"

    text_selector = "#post-"

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }
    }

    def parse(self, response):
        """
        Parse the main index page to extract article links and metadata.
        """
        # Select all article containers
        articles = response.css("li.li-has-thumb div.li-has-thumb__content")

        for article in articles:
            # Extract the article link
            article_url = article.css("a::attr(href)").get()

            # Extract metadata directly from the index page
            title = article.css(self.title_selector).get()
            author = article.css(self.author_selector).get()
            date = self.format_date(
                self.extract_date(article.css(self.date_selector).getall())
            )

            # Pass the extracted metadata via response meta
            meta = {
                "title": title,
                "author": author,
                "date": date,
            }

            # Follow the article link to extract full content
            if article_url:
                yield response.follow(article_url, self.parse_article, meta=meta)

    def parse_article(self, response):
        """
        Extract the full article content and combine it with metadata from the index.
        """

        item = {
            "title": response.meta.get("title"),
            "author": response.meta.get("author"),
            "date": response.meta.get("date"),
            "url": response.url,
            "text": "",
        }
        paragraph_texts = response.css(self.text_selector).get()

        item["text"] = paragraph_texts

        # Combine extracted metadata with the parsed content
        yield item

    def extract_date(self, text_parts):
        """Helper function to parse the date from metadata"""
        for part in text_parts:
            if "on" in part:  # Assuming the date starts after 'on'
                return part.strip().split("on")[-1].strip().rstrip(" in")
        return None

    def format_date(self, date_text):
        """Helper function to format date into dd-mm-yyyy"""
        try:
            parsed_date = datetime.strptime(date_text, "%B %d, %Y")
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            self.logger.error(f"Failed to parse date: {date_text}")
            return None
