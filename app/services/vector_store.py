from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from app.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_NAMESPACE_COCKTAILS,
    PINECONE_NAMESPACE_USER_MEMORIES,
    EMBEDDING_MODEL
)
import json
import uuid
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        try:
            # Initialize Pinecone with new API
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index_name = PINECONE_INDEX

            # Get the Pinecone index
            self.index = self.pc.Index(self.index_name)
            
            # Initialize the embeddings model
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            
            # Store namespaces
            self.cocktail_namespace = PINECONE_NAMESPACE_COCKTAILS
            self.memory_namespace = PINECONE_NAMESPACE_USER_MEMORIES
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {str(e)}")
            raise

    def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding for a text."""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def _process_cocktail_results(self, matches: List[Dict]) -> List[Dict[str, Any]]:
        """Process cocktail query results into a standardized format."""

        cocktails = []
        for match in matches:
            metadata = match['metadata']
            if match['score'] > 0.19:
                cocktails.append({
                    "metadata": metadata,
                    "score": match['score']
                })
            
        return cocktails

    def search_cocktails(self, query: str, limit: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for cocktails based on a query string."""
        try:
            # Generate embedding for the query
            query_embedding = self._get_embedding(query)
            
            # Simplify filter construction
            filter_dict = filters or {}
            
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                namespace=self.cocktail_namespace,
                filter=filter_dict,
                include_metadata=True
            )

            return self._process_cocktail_results(results['matches'])
        except Exception as e:
            logger.error(f"Error searching cocktails: {str(e)}")
            return []

    def store_user_memory(self, user_id: str, memory_data: Dict[str, Any]) -> Optional[str]:
        """Store user memory in the vector store."""
        try:
            memory_id = str(uuid.uuid4())
            memory_text = f"User {user_id} preferences: {json.dumps(memory_data)}"
            memory_embedding = self._get_embedding(memory_text)
            
            metadata = {
                "user_id": user_id,
                "text": memory_text,
                **memory_data
            }
            
            self.index.upsert(
                vectors=[(memory_id, memory_embedding, metadata)],
                namespace=self.memory_namespace
            )
            return memory_id
        except Exception as e:
            logger.error(f"Error storing user memory: {str(e)}")
            return None

    def get_user_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user memories from the vector store."""
        try:
            query_embedding = self._get_embedding(f"User {user_id} preferences")
            filter_dict = {"user_id": {"$eq": user_id}}
            
            results = self.index.query(
                vector=query_embedding,
                top_k=10,
                namespace=self.memory_namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            memories = []
            for match in results['matches']:
                metadata = match['metadata']
                content = metadata.get('text', f"User {user_id} preferences")
                memories.append({
                    "content": content,
                    "metadata": metadata,
                    "score": match['score']
                })
            return memories
        except Exception as e:
            logger.error(f"Error retrieving user memories: {str(e)}")
            return []

    def find_similar_cocktails(self, cocktail_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find cocktails similar to the given cocktail name."""
        try:
            cocktail_embedding = self._get_embedding(f"Cocktail similar to {cocktail_name}")
            
            results = self.index.query(
                vector=cocktail_embedding,
                top_k=limit,
                namespace=self.cocktail_namespace,
                include_metadata=True
            )
            
            return self._process_cocktail_results(results['matches'])
        except Exception as e:
            logger.error(f"Error finding similar cocktails: {str(e)}")
            return []
