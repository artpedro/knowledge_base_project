# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import redis
import json

class ArticlePipeline:
    def open_spider(self, spider):
        # Connect to Redis
        self.redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

    def process_item(self, item, spider):
        # Prepare data for queuing
        job_data = {
            "title": item["title"],
            "author": item["author"],
            "date": item["date"],
            "text": item["text"],
            "url": item["url"],

        }
        # Push data to the Redis queue
        self.redis_client.rpush("article_processing_queue", json.dumps(job_data))
        spider.logger.info(f"Pushed job to queue: {job_data['title']}")
        return item

    def close_spider(self, spider):
        spider.logger.info("Spider closed.")