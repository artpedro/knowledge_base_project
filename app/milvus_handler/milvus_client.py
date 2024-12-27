from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer
import logging


class MilvusClient:
    def __init__(self, host="localhost", port="19530", collection_name="ai_ml_knowledge"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dimension = 384  # Embedding vector dimension
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._connect()

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
        try:
            connections.connect(alias="default", host=self.host, port=self.port)
            logging.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to connect to Milvus: {e}")
            raise

    def _ensure_collection_ready(self):
        """
        Ensures the collection is created, indexed, and loaded into memory.
        """
        if not utility.has_collection(self.collection_name):
            logging.info(f"Collection '{self.collection_name}' does not exist. Creating...")
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="source_url", dtype=DataType.VARCHAR, max_length=512),
            ]
            schema = CollectionSchema(fields=fields, description="Knowledge collection")
            Collection(name=self.collection_name, schema=schema)
            logging.info(f"Collection '{self.collection_name}' created.")
        else:
            logging.info(f"Collection '{self.collection_name}' already exists.")

        # Ensure the collection is indexed
        collection = Collection(self.collection_name)
        if not collection.has_index():
            index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
            collection.create_index(field_name="vector", index_params=index_params)
            logging.info(f"Index created for collection '{self.collection_name}' with params: {index_params}")

        # Load the collection into memory
        collection.load()
        logging.info(f"Collection '{self.collection_name}' is loaded into memory.")

    def insert_data(self, titles, texts, category="General", source_url="N/A"):
        """
        Inserts documents into the collection with their embeddings, checking for duplicates.
        """
        self._ensure_collection_ready()

        if len(titles) != len(texts):
            raise ValueError("Titles and texts must have the same length.")

        collection = Collection(self.collection_name)

        # Track documents to insert and duplicates
        docs_to_insert = []
        skipped_count = 0

        for i in range(len(texts)):
            # Escape quotes in the text for the query expression
            escaped_text = texts[i].replace('"', '\\"')  # Escape quotes before using in the f-string
            expr = f'text == "{escaped_text}"'
            results = collection.query(expr, output_fields=["text"], limit=1)

            if not results:  # If no match is found
                docs_to_insert.append((titles[i], texts[i]))
            else:
                skipped_count += 1

        if docs_to_insert:
            # Combine title and text for embedding generation
            combined_docs = [f"{title}: {text}" for title, text in docs_to_insert]
            embeddings = [self.embedder.encode(doc).tolist() for doc in combined_docs]

            # Prepare data for insertion
            data = [
                {
                    "vector": embeddings[i],
                    "title": docs_to_insert[i][0],
                    "text": docs_to_insert[i][1],
                    "category": category,
                    "source_url": source_url,
                }
                for i in range(len(docs_to_insert))
            ]

            # Insert data into Milvus
            collection.insert(data)
            logging.info(f"Inserted {len(docs_to_insert)} documents into '{self.collection_name}'.")

            # Explicitly flush to persist data
            collection.flush()
            logging.info("Data flushed to disk.")
        else:
            logging.info("All documents were duplicates. Nothing inserted.")

        return len(docs_to_insert), skipped_count

    def search_similar(self, query_text, category_filter=None, limit=3):
        """
        Searches for similar text in the collection based on embeddings.
        """
        self._ensure_collection_ready()

        query_vector = self.embedder.encode(query_text).tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        expr = f"category == '{category_filter}'" if category_filter else None

        collection = Collection(self.collection_name)
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["title", "text", "category", "source_url"],
        )

        logging.info("Search Results:")
        for result in results:
            for match in result:
                logging.info(
                    f"Title: {match.entity.title}, Text: {match.entity.text}, "
                    f"Category: {match.entity.category}, URL: {match.entity.source_url}"
                )
        return results

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
