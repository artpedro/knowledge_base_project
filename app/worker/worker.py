import redis
import json
from app.cleaner.cleaner import Cleaner
from app.organizer.categorizer import Categorizer
from app.milvus_handler.milvus_client import MilvusClient

def process_article(job):
    # Initialize required components
    cleaner = Cleaner()
    categorizer = Categorizer()
    milvus_client = MilvusClient(host="milvus", port="19530")

    # Clean the text
    cleaned_text = cleaner.clean_text(job["text"])

    # Categorize the content
    categories = categorizer.categorize(cleaned_text)

    # Store in Milvus
    milvus_client.insert_data(
        titles=[job["title"]],
        texts=[cleaned_text],
        category=categories,
        source_url=job["url"]
    )

def main():
    # Connect to Redis
    redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

    while True:
        # Fetch a job from the queue
        job_data = redis_client.lpop("article_processing_queue")
        if not job_data:
            print("No jobs in the queue.")
            break

        job = json.loads(job_data)
        print(f"Processing job: {job['title']}")

        try:
            process_article(job)
        except Exception as e:
            print(f"Error processing job: {e}")