from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer

class MilvusLiteHandler:
    def __init__(self, db_path="../db/milvus_lite.db", collection_name="ai_ml_knowledge"):
        self.collection_name = collection_name
        self.db_path = db_path

        # Connect to Milvus Lite (local)
        self.client = MilvusClient(self.db_path)

        # Initialize embedding generator
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Define schema and initialize the collection
        self.dimension = 384  # Embedding vector dimension
        
        self.predefined_schema = MilvusClient.create_schema(auto_id=False,enable_dynamic_field=True)

        self.predefined_schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        self.predefined_schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dimension)
        self.predefined_schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=512)
        self.predefined_schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2048)
        self.predefined_schema.add_field(field_name="category", datatype=DataType.VARCHAR, max_length=256)
        self.predefined_schema.add_field(field_name="source_url", datatype=DataType.VARCHAR, max_length=512)
        
        self.create_collection()

    def create_collection(self):
        """
        Creates the collection with a predefined schema if it doesn't exist.
        """
        collections = self.client.list_collections()
        print(collections)
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=self.predefined_schema,
                dimension=self.dimension
            )
            print(f"Collection '{self.collection_name}' created with predefined schema.")
        else:
            print(f"Collection '{self.collection_name}' already exists.")

    def insert_data(self, titles, texts, category="General", source_url="N/A"):
        """
        Inserts documents into Milvus Lite with their embeddings, checking for duplicates.
        :param titles: List of document titles.
        :param texts: List of document texts.
        :param category: The topic/category for the documents.
        :param source_url: The source URL for the documents.
        :return: Tuple of (number of inserted documents, number of skipped duplicates)
        """
        if len(titles) != len(texts):
            raise ValueError("Titles and texts must have the same length.")
    
        # Track documents to insert and duplicates
        docs_to_insert = []
        skipped_count = 0
    
        for i in range(len(texts)):
            # Search for existing document with same text
            expr = f'text == "{texts[i]}"'
            results = self.client.query(
                collection_name=self.collection_name,
                filter_expr=expr,
                output_fields=["text"],
                limit=1
            )
            
            # If no matching document found, add to insertion list
            if len(results) == 0:
                docs_to_insert.append((titles[i], texts[i]))
            else:
                skipped_count += 1
    
        # If we have documents to insert, process them
        if docs_to_insert:
            # Combine title and text for embedding generation
            combined_docs = [f"{title}: {text}" for title, text in docs_to_insert]
            embeddings = [self.embedder.encode(doc).tolist() for doc in combined_docs]
    
            # Prepare data for insertion
            data = [
                {"vector": embeddings[i], 
                 "title": docs_to_insert[i][0], 
                 "text": docs_to_insert[i][1],
                 "category": category, 
                 "source_url": source_url}
                for i in range(len(docs_to_insert))
            ]
    
            # Insert into Milvus
            self.client.insert(collection_name=self.collection_name, data=data)
            print(f"Inserted {len(docs_to_insert)} documents into '{self.collection_name}'.")
            print(f"Skipped {skipped_count} duplicate documents.")
    
        else:
            print("All documents were duplicates. Nothing inserted.")
    
        return len(docs_to_insert), skipped_count
        

    def search_similar(self, query_text, category_filter=None, limit=3):
        """
        Searches for similar text in the collection based on embeddings.

        :param query_text: Query string to find similar content.
        :param category_filter: Optional filter for a specific category.
        :param limit: Number of results to retrieve.
        """
        query_vector = self.embedder.encode(query_text).tolist()
        filter_expression = f"category == '{category_filter}'" if category_filter else None
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            filter=filter_expression,
            limit=limit,
            output_fields=["title", "text", "category", "source_url"]
        )
        print("Search Results:")
        print(results)
        for result in results:
            print(result)
            for match in result:
                print(f"Title: {match['entity']['title']}")
                print(f"Text: {match['entity']['text']}")
                print(f"Category: {match['entity']['category']} | URL: {match['entity']['source_url']}")
                print("-" * 50)
        return results

    def query_by_filter(self, category_filter):
        """
        Queries all documents matching a specific category filter.

        :param category_filter: Filter expression for querying.
        """
        results = self.client.query(
            collection_name=self.collection_name,
            filter=f"category == '{category_filter}'",
            output_fields=["title", "text", "category", "source_url"]
        )
        print(f"Documents in category '{category_filter}':")
        for res in results:
            print(f"Title: {res['title']}")
            print(f"Text: {res['text']}")
            print(f"Category: {res['category']} | URL: {res['source_url']}")
            print("-" * 50)
        return results

    def count_documents(self):
        """
        Counts the number of documents in the collection.
        """
        stats = self.client.get_collection_stats(collection_name=self.collection_name)
        count = stats.get("row_count", 0)
        print(f"Collection '{self.collection_name}' contains {count} documents.")
        return count