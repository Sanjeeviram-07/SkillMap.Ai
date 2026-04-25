import logging
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Constants
CHROMA_DATA_PATH = "chroma_db"
COLLECTION_NAME = "learning_content"

class RAGService:
    def __init__(self):
        """
        Initializes the ChromaDB client and embedding function.
        """
        try:
            # Initialize ChromaDB persistent client
            self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
            
            # Initialize sentence-transformers embedding function
            # This uses the all-MiniLM-L6-v2 model by default or specified
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection with cosine similarity configuration
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"} # Use cosine similarity
            )
            logger.info("ChromaDB initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_document(self, doc_id: str, chunks: List[str], metadata: Optional[Dict[str, Any]] = None):
        """
        Stores document chunks in ChromaDB.
        
        Args:
            doc_id (str): Unique identifier for the document (e.g., filename).
            chunks (List[str]): List of text chunks to store.
            metadata (Optional[Dict[str, Any]]): Additional metadata for each chunk.
        """
        if not chunks:
            logger.warning(f"No chunks provided for document {doc_id}.")
            return

        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Prepare metadatas for each chunk
        metadatas = []
        for _ in range(len(chunks)):
            meta = (metadata or {}).copy()
            meta["doc_id"] = doc_id
            metadatas.append(meta)

        try:
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Added document '{doc_id}' with {len(chunks)} chunks to ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to add document '{doc_id}' to ChromaDB: {e}")
            raise

    def query(self, query_text: str, n_results: int = 3, filter: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Retrieves relevant chunks from ChromaDB for a given query.
        
        Args:
            query_text (str): The search query.
            n_results (int): Number of relevant chunks to return.
            filter (Optional[Dict[str, Any]]): Optional dictionary to filter results by metadata.
            
        Returns:
            List[str]: List of relevant text chunks.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter
            )
            if results and results['documents']:
                return results['documents'][0]
            return []
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def delete_document(self, doc_id: str):
        """
        Deletes all chunks associated with a document ID.
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
            logger.info(f"Deleted document '{doc_id}' from ChromaDB.")
        except Exception as e:
            logger.warning(f"Failed to delete document '{doc_id}': {e}")

# Reusable Instance (Lazy initialization to avoid overhead if not used)
_rag_instance = None

def get_rag_service() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
