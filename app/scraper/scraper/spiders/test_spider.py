import scrapy
from ..items import ArticleItem
import redis

class ArticlesSpider(scrapy.Spider):
    name = "articles"

    def start_requests(self):
        # Connect to Redis
        redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

        while True:
            # Fetch job from Redis queue
            job_id = redis_client.rpop("scrape_jobs")
            if not job_id:
                self.logger.info("No jobs in the queue.")
                break

            job = redis_client.hgetall(job_id)
            url = job["url"]
            category = job.get("category", "General")

            # Start scraping the job URL
            yield scrapy.Request(url, self.parse_article, meta={"category": category, "job_id": job_id})

    def parse_article(self, response):
        # Extract article content
        item = ArticleItem()
        item["title"] = response.css("h1.article-title::text").get()
        item["text"] = " ".join(response.css("div.article-body p::text").getall())
        item["url"] = response.url
        item["category"] = response.meta["category"]

        # Mark the job as complete in Redis
        job_id = response.meta["job_id"]
        redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
        redis_client.hset(job_id, "status", "completed")

        yield item