from flask import Blueprint, render_template, jsonify, request
from tests import run_all_tests
from app.retrieval import retrieve_and_generate
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
            "cleaner_tests": results.get("cleaner_tests", "Unknown"),
            "classifier_tests": results.get("classifier_tests", "Unknown"),
            "status": "Healthy" if all(v == "Passed" for v in results.values()) else "Unhealthy"
        }
    except Exception as e:
        status = {"status": "Unhealthy", "error": str(e)}

    return jsonify(status)


@main.route("/scrape", methods=["POST"])
def scrape():
    """
    Add a scraping job to the Redis queue or trigger all spiders.
    """
    if request.content_type == "application/json":
        # Handle JSON payload
        data = request.json or {}
    elif request.content_type == "application/x-www-form-urlencoded":
        # Handle form submission
        data = request.form.to_dict()
    else:
        # Unsupported Content-Type
        return jsonify({"status": "error", "message": "Unsupported Content-Type"}), 415

    url = data.get("url")
    if url:
        # Add a specific scraping job
        job = {"url": url}
        job_id = f"job_{redis_client.incr('job_counter')}"
        redis_client.hset(job_id, mapping=job)
        redis_client.lpush("scrape_jobs", job_id)
        return jsonify({"status": "success", "job_id": job_id}), 202
    else:
        # Trigger all spiders
        redis_client.publish("trigger_all_spiders", "run_all")
        return jsonify({"status": "success", "message": "All spiders triggered."}), 202



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
  
@main.route("/query", methods=["GET", "POST"])
def query_page():
    if request.method == "GET":
        return render_template("query.html")
    elif request.method == "POST":
        data = request.json
        print('post')
        user_query = data.get("query")
        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        try:
            response = retrieve_and_generate(user_query)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
