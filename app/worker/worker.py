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

    # Check for existing similar text
    existing_document = milvus_client.check_text_existence(
        cleaned_text, similarity_threshold=0.9
    )
    if existing_document:
        print(f"Duplicate document detected: {existing_document}")
        return  # Skip processing this article
    print("[INFO] CURRENT JOB NOT IN DATABASE")
    cand_cat = [
        "Natural Language Processing (NLP): syntax, semantics, tokenization, embeddings, transformers, chat interfaces, text generation, document summarization, entity recognition, language understanding, machine translation, conversational systems, text classification, language models, semantic search.",
        "Computer Vision: image analysis, visual data, object detection, facial recognition, segmentation, augmented reality, spatial computing, medical imaging, video tracking, 3D reconstruction, motion detection, scene understanding, object recognition, visual embeddings.",
        "Reinforcement Learning: reward-based learning, optimal policies, decision-making, autonomous control, trial-and-error strategies, deep Q-networks, policy optimization, exploration strategies, robotic navigation, environment simulation, reward shaping, Q-learning, multi-agent systems.",
        "Generative AI: synthetic content, creative synthesis, GANs, neural transformations, text-to-image, DALL·E, latent spaces, data augmentation, audio synthesis, visual content creation, style blending, deepfakes, content generation, generative transformers, text generation.",
        "AI Ethics and Bias: fairness, accountability, transparency, social impact, ethical challenges, privacy safeguards, algorithm discrimination, audit trails, ethical standards, responsible deployment, data protection, algorithm bias, inclusive AI, ethical AI frameworks.",
        "Autonomous Systems: real-time decisions, unmanned vehicles, robotics, industrial automation, adaptive control, dynamic environments, robotic swarms, sensor-driven systems, navigation algorithms, autonomous drones, real-time perception, control systems, self-driving technology.",
        "Time-Series Analysis: temporal trends, anomaly identification, forecasting techniques, sequential patterns, data cycles, seasonal variations, predictive analytics, multivariate trends, time-dependent modeling, stock analysis, trend detection, time-series clustering, periodicity analysis.",
        "Edge AI: localized processing, low-latency solutions, IoT integration, privacy-preserving methods, resource-efficient algorithms, real-time inference, embedded intelligence, on-device computation, distributed AI, compact networks, microcontrollers, edge computing.",
        "AI in Healthcare: diagnostic tools, genomics, personalized treatments, medical imaging advancements, drug discovery, clinical data analytics, patient monitoring, telemedicine innovations, wearable integration, predictive models, healthcare optimization, medical decision support, hospital management.",
        "Explainable AI (XAI): decision transparency, interpretability, feature attribution, causality, trust-building, Shapley values, LIME, visualization tools, diagnostic insight, interpretable outputs, explainability techniques, feature importance, sensitivity analysis.",
        "Federated Learning: distributed training, data privacy, decentralized computation, collaborative networks, secure aggregation, multi-device synchronization, cross-device training, localized updates, privacy-preserving AI, decentralized learning, edge collaboration, collaborative AI.",
        "Self-Supervised Learning: unlabeled data, contrastive techniques, representation extraction, pretraining, embedding alignment, self-labeling, masked language processing, unsupervised enrichment, latent pattern discovery, unsupervised pretraining, representation learning, feature discovery.",
        "AI in Creative Industries: art generation, music composition, storytelling, animation, creative augmentation, game design, digital synthesis, style adaptation, visual storytelling, immersive experiences, virtual production, generative storytelling, creative AI tools.",
        "ML Infrastructure and Engineering: operational pipelines, deployment frameworks, automation, scalable architecture, cloud integration, CI/CD, container orchestration, distributed systems, feature repositories, reproducibility, infrastructure optimization, production-ready pipelines, resource management.",
        "AI for Social Good: environmental monitoring, disaster preparedness, equitable access, conservation, renewable solutions, poverty alleviation, healthcare expansion, educational tools, sustainability efforts, social impact projects, societal challenges, resource allocation.",
        "Multimodal AI: text-image fusion, audio-visual synchronization, cross-modal integration, video analytics, multimodal embeddings, sensor data combination, natural interaction, voice-image analysis, cross-modal understanding, video-text models, speech and vision alignment.",
        "AI Hardware Optimization: GPU efficiency, parallel processing, neural accelerators, low-power computation, hardware-aware design, AI-specific processors, chip-level integration, inference acceleration, optimized computation, resource-efficient hardware, TPUs, custom AI chips.",
        "AI in Finance: trading algorithms, credit risk analytics, fraud detection, financial trends, portfolio optimization, transaction monitoring, robo-advisors, quantitative strategies, payment processing, investment forecasting, predictive analytics, algorithmic trading.",
        "Human-Centered AI: user interaction, adaptive interfaces, emotional intelligence, assistive technologies, accessibility features, human augmentation, usability design, inclusive frameworks, personalized interactions, emotion-aware systems, human-friendly interfaces, user-focused AI.",
        "Data Science: data preprocessing, analytics, visualization, statistical modeling, feature selection, database integration, dimensionality reduction, exploratory analysis, big data solutions, pattern recognition, descriptive statistics, clustering, regression analysis.",
    ]
    # Categorize the content
    categories = categorizer.categorize(
        cleaned_text, cand_cat, threshold=0.5, multi_label=True
    )
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
    redis_client = redis.StrictRedis(
        host=redis_host, port=redis_port, decode_responses=True
    )

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
