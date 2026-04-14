import os
import logging
from pinecone import Pinecone
from dotenv import load_dotenv

# Initialize logging for secure auditing and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_vector_database():
    """
    Deletes all existing vectors in the specified Pinecone index.
    
    This function acts as an administrative utility to wipe outdated 
    knowledge base entries (e.g., old 4x4 Tic-Tac-Toe data) before 
    upserting new 15x15 Gomoku strategies. It accesses environment 
    variables securely and performs a complete index flush.

    Raises:
        Exception: If the Pinecone API fails to authenticate or execute the deletion.
    """
    load_dotenv()
    
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    if not PINECONE_API_KEY:
        logger.error("Critical missing environment variable: PINECONE_API_KEY.")
        return

    try:
        # Initialize the Pinecone client
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Target the existing index from the project config
        index_name = "tictactoe-rag"
        index = pc.Index(index_name)
        
        logger.info(f"[ADMIN ACTION] Initiating deletion of all vectors in index: {index_name}")
        
        # Execute absolute deletion
        index.delete(delete_all=True)
        
        logger.info("✅ Successfully cleared all data from the Pinecone index.")
        
    except Exception as e:
        logger.error(f"Failed to clear Pinecone database: {str(e)}")

if __name__ == "__main__":
    clear_vector_database()