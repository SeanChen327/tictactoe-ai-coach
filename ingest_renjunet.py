"""
Data Ingestion Pipeline for RenjuNet RAG Knowledge Base.
"""
import os
import json
import logging
from google import genai
from google.genai.types import EmbedContentConfig
from pinecone import Pinecone
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_knowledge_base(json_filepath: str = "renjunet_knowledge.json") -> None:
    """
    Reads local JSON knowledge chunks and upserts them into Pinecone using Gemini Embeddings.
    This strictly mirrors the existing API calling patterns without modifying core app files.

    Args:
        json_filepath (str): Path to the JSON file containing the scraped knowledge.
    """
    load_dotenv()

    # Secure environment variable access
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    if not GEMINI_API_KEY or not PINECONE_API_KEY:
        logger.error("Critical API Keys are missing in .env file.")
        raise ValueError("API Keys are missing. Please set them in your environment.")

    # Initialize clients exactly as they are in existing architecture
    client = genai.Client(api_key=GEMINI_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("tictactoe-rag")

    if not os.path.exists(json_filepath):
        logger.error(f"Data file {json_filepath} not found. Please run the scraper first.")
        return

    # Load data
    with open(json_filepath, 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)

    logger.info(f"Starting embedding generation and Pinecone upsert for {len(knowledge_base)} items...")

    vectors_to_upsert = []
    for item in knowledge_base:
        try:
            # Exact API call format from original setup_db.py
            embedding_result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=item["text"],
                config=EmbedContentConfig(output_dimensionality=768)
            )
            vector_values = embedding_result.embeddings[0].values
            vectors_to_upsert.append((item["id"], vector_values, {"text": item["text"]}))
        except Exception as e:
            logger.warning(f"Failed to embed chunk {item['id']}: {str(e)}")

    # Batch upsert to Pinecone
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert)
        logger.info("✅ RenjuNet Knowledge base successfully embedded and uploaded to Pinecone!")
    else:
        logger.warning("No vectors were processed successfully.")

if __name__ == "__main__":
    ingest_knowledge_base()