# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from app.milvus_handler.milvus_client import MilvusClient
import os

class ArticlePipeline:
    def open_spider(self, spider):
        # Connect to Milvus using environment variables
        milvus_host = os.getenv("MILVUS_HOST", "localhost")
        milvus_port = os.getenv("MILVUS_PORT", "19530")
        self.client = MilvusClient(host=milvus_host, port=milvus_port)
        # Load categories from an external file
        self.categories = []
        categories_file_path = os.path.join(os.path.dirname(__file__), "categories.txt")
        with open(categories_file_path, "r") as file:
            self.categories = [line.strip() for line in file]


    def process_item(self, item, spider):
        # Clean and categorize the content
        categories = self.categorizer.categorize(item["text"], self.categories)

        # Insert data into Milvus
        self.client.insert_data(
            titles=[item["title"]],
            texts=[item["text"]],
            category=categories,
            source_url=item["url"]
        )
        return item


    def close_spider(self, spider):
        print("Finished processing articles.")