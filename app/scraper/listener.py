import redis
import subprocess
import os


def main():
    # Read Redis connection details from environment variables
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    # Connect to Redis
    redis_client = redis.StrictRedis(
        host=redis_host, port=redis_port, decode_responses=True
    )
    print(
        f"Listening to Redis at {redis_host}:{redis_port} on channel 'trigger_all_spiders'..."
    )

    # Subscribe to Redis channel
    pubsub = redis_client.pubsub()
    pubsub.subscribe("trigger_all_spiders")

    for message in pubsub.listen():
        if message["type"] == "message":
            command = message["data"]
            print(f"Received command: {command}")
            if command == "run_all":
                run_all_spiders()


def run_all_spiders():
    print("Running all Scrapy spiders...")
    try:
        # Trigger all spiders using Scrapy
        subprocess.run(["python", "scraper/extract_newspaper.py"])
        subprocess.run(["scrapy", "crawl", "kdnuggets"], check=True)

        print("All spiders executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running spiders: {e}")


if __name__ == "__main__":
    main()
