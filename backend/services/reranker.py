import os
import structlog
import cohere
from typing import List, Dict, Any

logger = structlog.get_logger()
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

class RerankerService:
    def __init__(self):
        if COHERE_API_KEY:
            self.co = cohere.AsyncClient(COHERE_API_KEY)
        else:
            self.co = None
            logger.warning("cohere_not_configured", message="COHERE_API_KEY is missing.")

    async def rerank_results(self, query: str, documents: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Takes the Top 30 documents from retrieval, sends them to Cohere, 
        and returns the Top N most relevant documents.
        """
        if not self.co:
            logger.error("rerank_failed_no_cohere")
            # Fallback to returning original top_n if no Cohere
            return documents[:top_n]
            
        if not documents:
            return []

        logger.info("reranking_documents", count=len(documents))
        
        # Cohere expects a list of strings or list of dicts with 'text'
        # We need to map our documents to string format
        doc_texts = []
        for doc in documents:
            # We must fetch the actual text content of the child chunk.
            # In our current setup, Pinecone returns metadata. 
            # Assuming 'text' is stored in Pinecone metadata during upsert.
            text_content = doc.get("metadata", {}).get("text", "")
            doc_texts.append(text_content)
            
        try:
            response = await self.co.rerank(
                query=query,
                documents=doc_texts,
                top_n=top_n,
                model='rerank-english-v3.0'
            )
            
            reranked_docs = []
            for result in response.results:
                original_doc = documents[result.index]
                # Enhance original doc with the new relevance score
                original_doc["rerank_score"] = result.relevance_score
                reranked_docs.append(original_doc)
                
            logger.info("reranking_complete", top_n_returned=len(reranked_docs))
            return reranked_docs
            
        except Exception as e:
            logger.error("cohere_rerank_failed", error=str(e))
            raise

reranker_service = RerankerService()
