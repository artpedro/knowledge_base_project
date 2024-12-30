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
    "Natural Language Processing (NLP): Covers techniques for analyzing, understanding, and generating human language. Includes tasks like sentiment analysis, chatbots, machine translation, and text summarization, commonly seen in research and applications for improving communication systems.",
    "Computer Vision: Focuses on processing and analyzing visual data such as images and videos. Tutorials and news often highlight topics like object detection, facial recognition, autonomous vehicles, and medical imaging advancements.",
    "Reinforcement Learning: Discusses agents learning optimal actions through trial-and-error interactions with an environment. Popular for robotics, autonomous systems, and gaming AI tutorials and breakthroughs.",
    "Generative AI: Includes creating synthetic content like text, images, or videos using models like GANs or transformers. News often reports on tools like ChatGPT, DALL·E, and advancements in generative technologies.",
    "AI Ethics and Bias: Examines fairness, accountability, and transparency in AI systems. News includes discussions on biased algorithms, ethical guidelines, and the societal impact of AI deployments.",
    "Autonomous Systems: Explores systems like drones, self-driving cars, and industrial robots that operate without human intervention. Tutorials often focus on combining AI with real-time sensors and decision-making.",
    "Time-Series Analysis: Focuses on analyzing sequential data like financial trends, weather forecasts, and sensor readings. News highlights innovations in forecasting algorithms and anomaly detection in AI systems.",
    "Edge AI: Refers to running AI models directly on devices like IoT hardware, smartphones, and sensors. Tutorials highlight applications in low-latency decision-making and privacy-focused AI deployment.",
    "AI in Healthcare: Covers AI-driven advancements in diagnostics, personalized medicine, medical imaging, and hospital management. News often highlights case studies or breakthrough models improving patient outcomes.",
    "Explainable AI (XAI): Focuses on making AI decisions interpretable by humans. Tutorials cover methods for visualizing model predictions, and news discusses trust and transparency in AI.",
    "Federated Learning: Discusses decentralized learning where AI models are trained across devices without sharing raw data. Tutorials emphasize privacy-preserving technologies and collaborative AI systems.",
    "Self-Supervised Learning: Covers AI models learning from unlabeled data to reduce reliance on manual annotations. News highlights innovations in pretraining techniques for natural language and vision tasks.",
    "AI in Creative Industries: Focuses on AI applications in art, music, and design. Tutorials often discuss creative tools like AI-assisted image generation and storytelling models.",
    "ML Infrastructure and Engineering: Covers building scalable systems for training, deploying, and managing AI models. Tutorials focus on topics like MLOps, containerization, and cloud-based AI deployments.",
    "AI for Social Good: Explores AI used to address global challenges like climate change, disaster response, and education. News features projects leveraging AI for public and environmental benefits.",
    "Adversarial Learning and Security: Discusses AI systems' robustness against malicious attacks. Tutorials often cover adversarial examples and techniques for securing machine learning models.",
    "Multimodal AI: Explores AI systems integrating text, images, audio, and video. Tutorials highlight applications like video understanding and multimodal embeddings for richer AI capabilities.",
    "AI Hardware Optimization: Focuses on hardware like GPUs, TPUs, and edge devices optimized for AI workloads. News includes advancements in hardware-efficient models and AI-specific chips.",
    "AI in Finance: Covers applications in fraud detection, algorithmic trading, credit risk analysis, and financial forecasting. Tutorials highlight AI tools used for predictive analytics and automation in finance.",
    "Human-Centered AI: Focuses on designing AI systems that prioritize human collaboration and usability. Tutorials discuss interfaces, accessibility, and aligning AI with user needs.",
    "Data Science: Encompasses AI-related techniques for analyzing and visualizing data. Tutorials often focus on data preprocessing, feature engineering, and using AI to uncover insights from large datasets."
]
    # Categorize the content
    categories = categorizer.categorize(cleaned_text,cand_cat,threshold=0.7,multi_label=True)
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