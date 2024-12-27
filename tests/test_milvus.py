import unittest
import uuid
from app.milvus_handler.milvus_client import MilvusClient
from pymilvus import utility


class TestMilvusClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up the Milvus client and clear the test collection before tests.
        """
        test_collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"  # Unique collection name
        cls.client = MilvusClient(collection_name=test_collection_name)
        cls.client.clear_collection()  # Clear the collection to start fresh
        cls.test_titles = ["Test Title 1", "Test Title 2"]
        cls.test_texts = ["Test text content 1.", "Test text content 2."]

    def test_connection(self):
        """
        Test if the Milvus client can connect to the database.
        """
        self.assertTrue(utility.has_collection(self.client.collection_name))
        print("[PASS] Connection test passed.")

    def test_collection_creation(self):
        """
        Test if the test collection is created and loaded.
        """
        self.client._ensure_collection_ready()
        self.assertTrue(utility.has_collection(self.client.collection_name))
        print("[PASS] Collection creation test passed.")

    def test_insert_documents(self):
        """
        Test inserting documents into the collection.
        """
        # Ensure collection is clear before testing
        self.client.clear_collection()

        # Insert data
        inserted_count, skipped_count = self.client.insert_data(
            self.test_titles, self.test_texts
        )
        
        self.assertEqual(inserted_count, len(self.test_titles))
        self.assertEqual(skipped_count, 0)
        print(f"[PASS] Insert documents test passed. Inserted: {inserted_count}, Skipped: {skipped_count}")

    def test_duplicate_detection(self):
        """
        Test that duplicates are correctly detected and skipped.
        """
        self.client.insert_data(self.test_titles, self.test_texts)  # Initial insert
        inserted_count, skipped_count = self.client.insert_data(
            self.test_titles, self.test_texts
        )  # Attempt duplicate insert
        self.assertEqual(inserted_count, 0)
        self.assertEqual(skipped_count, len(self.test_titles))
        print("[PASS] Duplicate detection test passed.")

    def test_document_count(self):
        """
        Test the count of documents in the collection.
        """
        self.client.insert_data(self.test_titles, self.test_texts)  # Initial insert
        total_documents = self.client.count_documents()
        self.assertEqual(total_documents, len(self.test_titles))
        print(f"[PASS] Document count test passed. Total documents: {total_documents}")

    def test_search_documents(self):
        """
        Test searching for similar documents in the collection.
        """
        self.client.insert_data(self.test_titles, self.test_texts)  # Ensure data exists
        query_text = self.test_texts[0]
        results = self.client.search_similar(query_text, limit=1)
        self.assertGreater(len(results), 0)
        print("[PASS] Search documents test passed.")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up by dropping the test collection.
        """
        if utility.has_collection(cls.client.collection_name):
            utility.drop_collection(cls.client.collection_name)
            print(f"[INFO] Test collection '{cls.client.collection_name}' dropped.")

if __name__ == "__main__":
    unittest.main()
