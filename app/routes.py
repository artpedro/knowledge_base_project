from flask import Blueprint, render_template, jsonify, request
from tests import run_all_tests
import subprocess
import unittest
import redis

# Create a blueprint for the application routes
main = Blueprint("main", __name__)

# Connect to Redis
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)


@main.route("/")
def home():
    """
    Render the home page.
    """
    return render_template("home.html")

@main.route("/health")
def health():
    """
    Perform health checks for the Flask app and database.
    """
    try:
        # Run all tests and get the results
        results = run_all_tests()
        status = {
            "flask_tests": results.get("flask_tests", "Unknown"),
            "database_tests": results.get("database_tests", "Unknown"),
            "status": "Healthy" if all(v == "Passed" for v in results.values()) else "Unhealthy"
        }
    except Exception as e:
        status = {"status": "Unhealthy", "error": str(e)}

    return jsonify(status)


@main.route("/scrape", methods=["POST"])
def scrape():
    """
    Add a scraping job to the Redis queue.
    """
    data = request.json
    if not data or "url" not in data:
        return jsonify({"status": "error", "message": "URL is required."}), 400

    job = {"url": data["url"], "category": data.get("category", "General")}
    job_id = f"job_{redis_client.incr('job_counter')}"  # Generate a unique job ID

    redis_client.hset(job_id, mapping=job)  # Store job details in Redis
    redis_client.lpush("scrape_jobs", job_id)  # Add job ID to the queue

    return jsonify({"status": "success", "job_id": job_id}), 202


@main.route("/scrape_status/<job_id>", methods=["GET"])
def scrape_status(job_id):
    """
    Get the status of a specific scraping job.
    """
    if redis_client.exists(job_id):
        job = redis_client.hgetall(job_id)
        return jsonify({"status": "success", "job": job})
    else:
        return jsonify({"status": "error", "message": "Job not found."}), 404