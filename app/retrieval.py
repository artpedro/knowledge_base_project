from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from app.milvus_handler.milvus_client import MilvusClient

# Load environment variables from the .env file
load_dotenv()

# Constants for configuration
MILVUS_HOST = "standalone"
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY)
print(MILVUS_HOST)
collection_name = "ai_ml_knowledge"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")

PROMPT = """
Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.
<context>
{context}
</context>
<question>
{question}
</question>
"""


def initialize_milvus_vectorstore():
    """
    Initialize the Milvus vector store using LangChain integration.
    """
    milvus = MilvusClient(host=MILVUS_HOST, port=MILVUS_PORT)
    return milvus


def retrieve_and_generate(query):
    """
    Retrieve relevant documents from Milvus and generate a response using OpenAI's API.
    Args:
        query (str): The user's input query.

    Returns:
        str: The generated response.
    """
    # Initialize the vector store and retriever
    milvus_client = initialize_milvus_vectorstore()
    # Query database
    search_res = milvus_client.search_similar(query, category_filter=None, limit=3)

    # Loading content
    context = ""
    for i in search_res:
        context += i["text"] + "\n"
    print(context)

    # Generate response
    prompt = PROMPT.format(context=context, question=query)
    response = model.invoke([{"role": "system", "content": prompt}])

    return response.content
