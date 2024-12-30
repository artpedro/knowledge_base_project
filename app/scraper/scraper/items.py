import scrapy

class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    text = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()