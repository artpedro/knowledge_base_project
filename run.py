from flask import Flask
from app.routes import main
from config import Config
import os


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "app/templates"),
    )
    app.config.from_object(Config)
    app.register_blueprint(main)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
