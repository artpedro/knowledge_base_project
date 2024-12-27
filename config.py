import os

class Config:
    DEBUG = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    EMBEDDINGS_DIR = os.getenv("EMBEDDINGS_DIR", "./embeddings")
