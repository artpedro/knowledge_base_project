import newspaper
from newspaper import Article
import redis
import json
from datetime import datetime

# Links to extract articles from
links = ["https://towardsdatascience.com/latest", "https://bair.berkeley.edu/blog/"]

# Redis connection setup
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

# File to track the last request date
log_file = "last_date.log"


def get_last_date():
    try:
        with open(log_file, "r") as file:
            return datetime.strptime(file.read().strip(), "%Y-%m-%d")
    except FileNotFoundError:
        return datetime.min


def update_last_date(date):
    with open(log_file, "w") as file:
        file.write(date.strftime("%Y-%m-%d"))


def extract_articles(link):
    source = newspaper.build(link, memoize_articles=False, fetch_images=False)
    articles = []

    for article in source.articles[:3]:
        try:
            article.download()
            article.parse()
            print(article.title)
            articles.append(
                {
                    "title": article.title or "Unknown Title",
                    "author": article.authors[0] or "Unknown Author",
                    "date": article.publish_date,
                    "url": article.url,
                    "text": article.text or "",
                }
            )
        except Exception as e:
            print(f"Error processing article: {e}")

    return articles


def send_to_redis(article):
    job_data = {
        "title": article["title"],
        "author": article["author"],
        "date": article["date"].strftime("%Y-%m-%d") if article["date"] else None,
        "url": article["url"],
        "text": article["text"],
    }
    redis_client.rpush("article_processing_queue", json.dumps(job_data))
    print(f"Pushed to Redis: {job_data['title']}")


from datetime import datetime


def make_naive(dt):
    """Convert an offset-aware datetime to offset-naive."""
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


def main():
    last_date = get_last_date()
    print(f"Last request date: {last_date}")

    all_articles = []
    for link in links:
        print(f"Processing link: {link}")
        articles = extract_articles(link)
        all_articles.extend(articles)

    # Normalize all dates to naive for comparison
    new_articles = [
        a for a in all_articles if a["date"] and make_naive(a["date"]) > last_date
    ]

    for article in new_articles:
        send_to_redis(article)

    if new_articles:
        latest_date = max(make_naive(a["date"]) for a in new_articles if a["date"])
        update_last_date(latest_date)
        print(f"Updated last request date to: {latest_date}")
    else:
        print("No new articles found.")


if __name__ == "__main__":
    main()
