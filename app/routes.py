from flask import Blueprint, render_template,jsonify
from tests import run_all_tests  # We'll create this function.
import unittest

# Create a blueprint for the application routes
main = Blueprint("main", __name__)

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