from flask import Blueprint, render_template

# Create a blueprint for the application routes
main = Blueprint("main", __name__)

@main.route("/")
def home():
    """
    Render the home page.
    """
    return render_template("home.html")

# Add more routes as needed