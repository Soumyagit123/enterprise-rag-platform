import os
import structlog
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec

logger = structlog.get_logger()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "enterprise-rag-index")

class VectorStoreService:
    def __init__(self):
        if PINECONE_API_KEY:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            
            try:
                # Automatically create the index if it doesn't exist
                existing_indexes = [idx.name for idx in self.pc.list_indexes()]
                if PINECONE_INDEX_NAME not in existing_indexes:
                    logger.info("creating_pinecone_index", name=PINECONE_INDEX_NAME)
                    self.pc.create_index(
                        name=PINECONE_INDEX_NAME,
                        dimension=3072,
                        metric="dotproduct",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    logger.info("pinecone_index_created", name=PINECONE_INDEX_NAME)
            except Exception as e:
                logger.warning("pinecone_auto_create_failed_or_skipped", error=str(e))
                
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
        else:
            self.pc = None
            self.index = None
            logger.warning("pinecone_not_configured", message="PINECONE_API_KEY is missing.")

    def store_chunks(self, chunks: List[Dict[str, Any]], tenant_id: str):
        """
        Upsert vectors into Pinecone using tenant_id as the namespace for isolation.
        """
        if not self.index:
            logger.error("store_failed_no_pinecone")
            return
            
        logger.info("storing_vectors", count=len(chunks), tenant_id=tenant_id)
        
        vectors_to_upsert = []
        for chunk in chunks:
            vectors_to_upsert.append({
                "id": chunk["id"],
                "values": chunk["values"],
                "metadata": chunk["metadata"]
            })
            
        try:
            self.index.upsert(vectors=vectors_to_upsert, namespace=tenant_id)
            logger.info("vectors_upserted_successfully", count=len(vectors_to_upsert), namespace=tenant_id)
        except Exception as e:
            logger.error("vector_upsert_failed", error=str(e))
            raise

vector_store = VectorStoreService()
