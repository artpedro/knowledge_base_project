from flask import Blueprint, jsonify

def setup_routes(app):
    @app.route("/")
    def home():
        return jsonify({"message": "Flask backend is running!"})

    # Add more routes here
