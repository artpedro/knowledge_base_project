import os

class Config:
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
