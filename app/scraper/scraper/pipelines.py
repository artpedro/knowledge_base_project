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

    def process_item(self, item, spider):
        # Insert data into Milvus
        self.client.insert_data(
            titles=[item["title"]],
            texts=[item["text"]],
            category=item["category"],
            source_url=item["url"]
        )
        return item

    def close_spider(self, spider):
        print("Finished processing articles.")