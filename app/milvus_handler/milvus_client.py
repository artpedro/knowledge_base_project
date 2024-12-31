
from datetime import datetime
from dateutil import parser
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
import time
import os

class MilvusClient:
    def __init__(self, host=None, port=None, collection_name="ai_ml_knowledge"):
        self.host = host or os.getenv("MILVUS_HOST", "standalone")
        self.port = port or os.getenv("MILVUS_PORT", "19530")
        self.collection_name = collection_name
        self.dimension = 384  # Embedding vector dimension
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Pre-trained model for embeddings
        self._connect()
        self._ensure_collection_ready()

    def clear_collection(self):
        """
        Drops and recreates the collection to ensure a clean state.
        """
        if utility.has_collection(self.collection_name):
            logging.info(f"Dropping collection '{self.collection_name}'...")
            utility.drop_collection(self.collection_name)
        self._ensure_collection_ready()
        logging.info(f"Collection '{self.collection_name}' cleared and recreated.")

    def _connect(self):
        """
        Connect to Milvus server.
        """
        try:
            connections.connect(alias="default", host=self.host, port=self.port)
            logging.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to connect to Milvus: {e}")
            raise

    from pymilvus import utility

    def _ensure_collection_ready(self):
        """
        Ensures the collection is created, indexed, and loaded into memory.
        """
        if not utility.has_collection(self.collection_name):
            logging.info(f"Collection '{self.collection_name}' does not exist. Creating...")
            # Define the schema for the collection
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
                FieldSchema(name="author", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=10),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=20000),
                FieldSchema(name="categories", dtype=DataType.JSON),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            ]
            schema = CollectionSchema(fields=fields, description="Knowledge collection with metadata and vector embeddings")
            Collection(name=self.collection_name, schema=schema)
            logging.info(f"Collection '{self.collection_name}' created.")
        else:
            logging.info(f"Collection '{self.collection_name}' already exists.")

        collection = Collection(self.collection_name)

        # Check if an index exists, create it if missing
        if not collection.has_index():
            logging.info("Index not found. Creating index...")
            index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
            collection.create_index(field_name="vector", index_params=index_params)
            logging.info("Index creation initiated. Waiting for completion...")

            # Wait for index creation to complete
            while not collection.has_index():
                logging.info("Waiting for index to be ready...")
                time.sleep(1)

        # Explicitly load the collection into memory
        logging.info("Loading collection into memory...")
        collection.load()
        logging.info(f"Collection '{self.collection_name}' is loaded into memory.")

    def insert_data(self, title, author, date, text, categories):
        """
        Inserts a single document into the collection, including its vector embedding.
        """
        self._ensure_collection_ready()

        collection = Collection(self.collection_name)

        # Convert the date into a consistent format
        try:
            # Parse the date using dateutil.parser
            parsed_date = parser.parse(date)
            # Convert to the desired format
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            formatted_date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError as e:
            logging.error(f"Invalid date format: {date}. Error: {e}")
            raise ValueError("Date must be in 'dd-mm-yyyy' format")

        # Check for duplicate text
        escaped_text = text.replace('"', '\\"')
        expr = f'text == "{escaped_text}"'
        results = collection.query(expr, output_fields=["text"], limit=1)

        if results:
            logging.info("Duplicate text detected. Skipping insertion.")
            return {"status": "skipped", "message": "Duplicate text detected"}

        # Generate embedding for the text
        embedding = self.embedder.encode(text).tolist()

        # Insert the new document
        data = [
            {
                "title": title,
                "author": author,
                "date": formatted_date,
                "text": text,
                "categories": categories,
                "vector": embedding,
            }
        ]
        collection.insert(data)
        collection.flush()
        logging.info("Document inserted successfully.")
        return {"status": "success", "message": "Document inserted"}

    def search_similar(self, query_text, category_filter=None, limit=3):
        """
        Searches for similar text in the collection based on embeddings.
        """
        self._ensure_collection_ready()
        query_vector = self.embedder.encode(query_text).tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        expr = None

        if category_filter:
            expr = f'categories LIKE "%{category_filter}%"'

        collection = Collection(self.collection_name)
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["title", "author", "date", "text", "categories"],
        )

        formatted_results = []
        for result in results[0]:
            formatted_results.append({
                "title": result.entity.title,
                "author": result.entity.author,
                "date": result.entity.date,
                "text": result.entity.text,
                "categories": result.entity.categories,
                "distance": result.distance,
            })

        logging.info("Search completed.")
        return formatted_results
    
    def check_text_existence(self, text, similarity_threshold=0.9):
        """
        Checks if the provided text has a similar instance in the database.

        Parameters:
            text (str): The text to check for similarity.
            similarity_threshold (float): The similarity score threshold to consider it as existing.

        Returns:
            dict: A dictionary containing the most similar text and its similarity score if found,
                or None if no similar text meets the threshold.
        """
        self._ensure_collection_ready()

        # Generate embedding for the input text
        query_vector = self.embedder.encode(text).tolist()

        # Search for the most similar text
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}  
        collection = Collection(self.collection_name)
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=1,  # Only return the most similar result
            output_fields=["text", "title", "author", "date", "categories"]
        )

        if results[0]:
            top_result = results[0][0]  # Get the top result
            similarity_score = 1 - top_result.distance  # Convert distance to similarity score for IP metric

            if similarity_score >= similarity_threshold:
                return {
                    "text": top_result.entity.get("text"),
                    "title": top_result.entity.get("title"),
                    "author": top_result.entity.get("author"),
                    "date": top_result.entity.get("date"),
                    "categories": top_result.entity.get("categories"),
                    "similarity_score": similarity_score
                }

        return None  # No similar text found above the threshold
    def count_documents(self):
        """
        Counts the number of documents in the collection.
        """
        self._ensure_collection_ready()

        collection = Collection(self.collection_name)
        count = collection.num_entities  # Get the total number of entities
        logging.info(f"Collection '{self.collection_name}' contains {count} documents.")
        return count

    def count_documents(self):
        """
        Counts the number of documents in the collection.
        """
        self._ensure_collection_ready()

        collection = Collection(self.collection_name)
        count = collection.num_entities  # Get the total number of entities
        logging.info(f"Collection '{self.collection_name}' contains {count} documents.")
        return count


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

    client = MilvusClient()

    # Insert sample data
    print("\n[INFO] Inserting sample data into the collection...")
    titles = ["Title 4", "Title 5", "Title 6"]
    texts = [
        "This is the forth text.",
        "This is the fifth text.",
        "This is the sixth text about Milvus."
    ]
    inserted_count, skipped_count = client.insert_data(titles, texts)
    print(f"[INFO] Inserted {inserted_count} documents, skipped {skipped_count} duplicates.")

    # Search for similar text
    print("\n[INFO] Searching for documents similar to a query text...")
    query_text = "This is"
    search_results = client.search_similar(query_text, limit=3)
    print(f"[INFO] Found {len(search_results)} search results.")

    # Count documents
    print("\n[INFO] Counting the total number of documents in the collection...")
    total_documents = client.count_documents()
    print(f"[INFO] The collection contains {total_documents} documents.")
