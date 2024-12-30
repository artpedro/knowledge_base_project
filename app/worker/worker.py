import os
import redis
import json
from cleaner.cleaner import TextCleaner
from organizer.categorizer import ContentCategorizer
from milvus_handler.milvus_client import MilvusClient

def process_article(job):
    # Initialize required components
    cleaner = TextCleaner()
    categorizer = ContentCategorizer()
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    milvus_port = os.getenv("MILVUS_PORT", "19530")
    milvus_client = MilvusClient(host=milvus_host, port=milvus_port)

    # Clean the text
    cleaned_text = cleaner.clean_text(job["text"])
    cand_cat = ["Natural Language Processing (NLP)",
"Computer Vision",
"Reinforcement Learning",
"Generative AI",
"AI Ethics and Bias",
"Autonomous Systems",
"Time-Series Analysis",
"Edge AI",
"AI in Healthcare",
"Explainable AI (XAI)",
"Federated Learning",
"Self-Supervised Learning",
"AI in Creative Industries",
"ML Infrastructure and Engineering",
"AI for Social Good",
"Adversarial Learning and Security",
"Multimodal AI",
"AI Hardware Optimization",
"AI in Finance",
"Human-Centered AI",
"Data Science"]
    # Categorize the content
    categories = categorizer.categorize(cleaned_text,cand_cat)
    print(categories)
    # Store in Milvus
    milvus_client.insert_data(
        titles=[job["title"]],
        texts=[cleaned_text],
        category=categories,
        source_url=job["url"]
    )
def check_redis_connection(redis_client):
    try:
        redis_client.ping()
        print("[PASS] Redis connection is healthy.")
    except redis.ConnectionError as e:
        print(f"[ERROR] Redis connection failed: {e}")
        raise

def check_milvus_connection(milvus_host, milvus_port):
    try:
        milvus_client = MilvusClient(host=milvus_host, port=milvus_port)
        print("[PASS] Milvus connection is healthy.")
    except Exception as e:
        print(f"[ERROR] Milvus connection failed: {e}")
        raise

def main():
    # Connect to Redis
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Health checks
    check_redis_connection(redis_client)
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    milvus_port = os.getenv("MILVUS_PORT", "19530")
    check_milvus_connection(milvus_host, milvus_port)

    while True:
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