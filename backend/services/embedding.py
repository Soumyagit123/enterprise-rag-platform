import os
import structlog
import numpy as np
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = structlog.get_logger()

class EmbeddingService:
    def __init__(self):
        # Requires GOOGLE_API_KEY environment variable
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    def normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalizes embeddings for optimal cosine similarity."""
        vec = np.array(vector)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vector
        return (vec / norm).tolist()

    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes chunks (dictionaries) with 'content', 'id', 'metadata'.
        Returns them augmented with 'values' (the normalized embedding).
        """
        logger.info("generating_embeddings", count=len(chunks))
        
        texts = [chunk["content"] for chunk in chunks]
        
        try:
            # Generate embeddings in batch
            vectors = await self.embeddings.aembed_documents(texts)
            
            for chunk, vector in zip(chunks, vectors):
                chunk["values"] = self.normalize_vector(vector)
                
            return chunks
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e))
            raise

embedding_service = EmbeddingService()
