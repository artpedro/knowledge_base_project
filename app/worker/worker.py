import os
import redis
import json
import time
from cleaner.cleaner import TextCleaner
from organizer.categorizer import ContentCategorizer
from milvus_handler.milvus_client import MilvusClient
print("Starting worker...")
import sys
print(f"Python Path: {sys.path}")

def process_article(job, cleaner, categorizer):
    # Initialize required components
    
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    milvus_port = os.getenv("MILVUS_PORT", "19530")
    milvus_client = MilvusClient(host=milvus_host, port=milvus_port)

    # Clean the text
    cleaned_text = cleaner.clean_text(job["text"])
    print("Clean text:", cleaned_text)
    cand_cat = [
    "Natural Language Processing (NLP): human language, sentiment analysis, chatbots, machine translation, text summarization, communication systems.",
    "Computer Vision: visual data, images, videos. object detection, facial recognition, autonomous vehicles, medical imaging advancements.",
    "Reinforcement Learning: agents learning, optimal actions, trial-and-error interactions, robotics, autonomous systems, gaming AI.",
    "Generative AI: synthetic content, text, images, videos, GANs, transformers, ChatGPT, DALL·E, generative",
    "AI Ethics and Bias: fairness, accountability, transparency in AI systems. biased algorithms, ethical guidelines, societal impact",
    "Autonomous Systems: drones, self-driving cars, industrial robots, without human intervention, real-time sensors, decision-making.",
    "Time-Series Analysis: sequential data, financial trends, weather forecasts, sensor readings. forecasting, anomaly detection",
    "Edge AI: IoT hardware, smartphones,sensors, low-latency, privacy-focused",
    "AI in Healthcare: diagnostics, personalized medicine, medical imaging, hospital management, patient outcomes.",
    "Explainable AI (XAI): interpretable, visualizing model predictions, trust, transparency",
    "Federated Learning: decentralized learning, trained across devices, privacy-preserving, collaborative",
    "Self-Supervised Learning: unlabeled data, pretraining techniques",
    "AI in Creative: art, music,design, creative, storytelling",
    "ML Infrastructure and Engineering: building scalable systems, training, deploying, managing, MLOps, containerization, cloud-based",
    "AI for Social: global challenges, climate change, disaster response, education. public, environmental",
    "Multimodal AI: integrating text, images, audio, video. video understanding, multimodal embeddings,richer AI capabilities.",
    "AI Hardware Optimization: hardware, GPUs, TPUs, workloads, hardware-efficient, AI-specific chips.",
    "AI in Finance: algorithmic trading, credit risk, financial forecasting, automation in finance.",
    "Human-Centered AI: human collaboration, usability, interfaces, accessibility, user needs.",
    "Data Science: analyzing, visualizing data, data preprocessing, feature engineering, insights"
]
    # Categorize the content
    categories = categorizer.categorize(cleaned_text,cand_cat,threshold=0.5,multi_label=True)
    categories = [categories.split(":")[0] for categories in categories]
    print(categories)
    # Store in Milvus
    try:
        result = milvus_client.insert_data(
            title=job["title"],
            author=job["author"],
            date=job["date"],
            text=cleaned_text,
            categories=categories,
        )
        print(f"Inserted article: {result}")
    except Exception as e:
        print(f"Error inserting article: {e}")

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
    print("connecting to redis")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Health checks
    print("checking redis connection")
    check_redis_connection(redis_client)
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    milvus_port = os.getenv("MILVUS_PORT", "19530")
    print("checking milvus connection")
    check_milvus_connection(milvus_host, milvus_port)
    cleaner = TextCleaner()
    print("text cleaner initilized")
    categorizer = ContentCategorizer()
    print("content categorizer initilized")
    while True:
        try:
            print("popping job")
            job_data = redis_client.lpop("article_processing_queue")
            print(f"Job data: {job_data}")
            if not job_data:
                print("No jobs in the queue.")
                time.sleep(5)  # Avoid busy looping
                continue

            job = json.loads(job_data)
            print(f"Processing job: {job}")
            process_article(job, cleaner, categorizer)

        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}")
            time.sleep(5)  # Retry after a delay
        except json.JSONDecodeError as e:
            print(f"Invalid job format: {e}")
        except Exception as e:
            print(f"Unhandled error: {e}")

if __name__ == "__main__":
    
    main()