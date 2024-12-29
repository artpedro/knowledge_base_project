import scrapy
from ..items import ArticleItem


class KDnuggetsSpider(scrapy.Spider):
    name = "kdnuggets"
    allowed_domains = ["kdnuggets.com"]
    start_urls = ["https://www.kdnuggets.com/news/index.html"]

    def parse(self, response):
        """
        Parse the main page and extract all links from the targeted unordered list (`<ul>`).
        Follow each link to extract full article content.
        """
        articles = response.css("ul li.li-has-thumb div.li-has-thumb__content")

        for article in articles:
            title = article.css("a::text").get()
            url = article.css("a::attr(href)").get()
            meta_data = {
                "title": title,
                "author": article.css("div.author-link a::text").get(default="").strip(),
                "category": article.css("div.author-link a[href*='/tag/']::text").get(default="").strip(),
                "date": article.css("div.author-link::text").re_first(r"on (.+) in"),
            }

            # Follow the link to the full article
            yield response.follow(
                url, callback=self.parse_article, meta=meta_data
            )

    def parse_article(self, response):
        """
        Extract the text content from the <p> tags of the main content area of the article.
        """
        # Extract all <p> text from the main content area
        paragraphs = response.css("#content p::text").getall()
        content = "\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())

        # Yield the full article item
        yield ArticleItem(
            title=response.meta["title"],
            text=content,
            url=response.url,
            meta={
                "author": response.meta.get("author"),
                "category": response.meta.get("category"),
                "date": response.meta.get("date"),
            },
        )