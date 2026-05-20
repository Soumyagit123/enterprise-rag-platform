import structlog
import asyncio
from typing import List, Dict, Any
from pinecone_text.sparse import BM25Encoder
from .vector_store import vector_store
from .embedding import embedding_service
from .reranker import reranker_service
from .redis_client import redis_client
from .cache import semantic_cache

logger = structlog.get_logger()

class HybridRetrievalService:
    def __init__(self):
        self.bm25 = BM25Encoder()
        # Initialize locally with a basic corpus to prevent external network calls and startup hangs
        self.bm25.fit([
            "The quick brown fox jumps over the lazy dog",
            "Retrieval-Augmented Generation processes enterprise documents",
            "FastAPI backend with Redis semantic cache and Pinecone vector database",
            "RabbitMQ queues ingestion tasks for asynchronous processing",
            "Docker containers orchestrate backend, frontend, and database services"
        ])

    async def _get_dense_vector(self, query: str) -> List[float]:
        # Generate the dense embedding using Gemini
        # We wrap the query in a dictionary as expected by the embedding_service 
        # but just extract the embedding.
        chunk = [{"content": query, "id": "query", "metadata": {}}]
        embedded = await embedding_service.generate_embeddings(chunk)
        return embedded[0]["values"]

    def _get_sparse_vector(self, query: str) -> Dict[str, Any]:
        # Generate sparse vector for exact keyword matches
        # This executes synchronously but we can wrap it if it gets heavy
        sparse = self.bm25.encode_queries(query)
        return sparse

    def _merge_and_deduplicate(self, dense_results: List[dict], sparse_results: List[dict], alpha: float = 0.5) -> List[dict]:
        """
        Merge results from dense and sparse search.
        Since Pinecone hybrid search does this natively if queried together, we can actually
        just use Pinecone's built-in hybrid querying, but if we query two separate indices/databases
        we would use Reciprocal Rank Fusion (RRF) or score weighting here.
        
        Assuming we manually queried two indices for demonstration:
        """
        combined = {}
        
        # Helper to process results
        def process_results(results, weight):
            for rank, match in enumerate(results):
                doc_id = match['id']
                if doc_id not in combined:
                    combined[doc_id] = {
                        "id": doc_id,
                        "score": 0.0,
                        "metadata": match.get("metadata", {})
                    }
                # RRF calculation: weight / (rank + 60)
                combined[doc_id]["score"] += weight * (1.0 / (rank + 60))

        process_results(dense_results, alpha)
        process_results(sparse_results, 1 - alpha)
        
        # Sort by combined score
        sorted_results = sorted(combined.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:15]  # Reduced from 30 → 15 for faster reranking

    async def retrieve(self, query: str, tenant_id: str, top_k: int = 15) -> List[dict]:  # Reduced from 30 → 15
        """
        Main entrypoint for hybrid retrieval.
        It runs Dense and Sparse encoding in parallel, then queries Pinecone.
        """
        logger.info("starting_hybrid_retrieval", query=query, tenant_id=tenant_id)

        # --- LEVEL 2 OPTIMIZATION: Check retrieval cache before hitting Pinecone + Cohere ---
        cached_retrieval = await semantic_cache.check_retrieval_cache(query)
        if cached_retrieval:
            logger.info("retrieval_cache_hit_skipping_pinecone_and_cohere", query=query)
            return cached_retrieval
        
        # 1. Parallel Generation of Dense and Sparse vectors
        dense_task = asyncio.create_task(self._get_dense_vector(query))
        
        # Running synchronous BM25 encode in a thread to prevent blocking
        loop = asyncio.get_event_loop()
        sparse_task = loop.run_in_executor(None, self._get_sparse_vector, query)
        
        dense_vec, sparse_vec = await asyncio.gather(dense_task, sparse_task)
        
        if not vector_store.index:
            logger.error("pinecone_not_available")
            return []
            
        # 2. Query Pinecone
        # If Pinecone is configured with a hybrid index, we can pass both vectors in one call.
        try:
            # Note: Pinecone Serverless supports sparse vectors directly via `sparse_vector` arg.
            response = vector_store.index.query(
                vector=dense_vec,
                sparse_vector=sparse_vec,
                namespace=tenant_id,
                top_k=top_k,
                include_metadata=True
            )
            
            # 3. Format initial Top 30 results
            results = []
            for match in response.get("matches", []):
                results.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                })
                
            logger.info("hybrid_retrieval_complete", results_count=len(results))
            
            # 4. Rerank using Cohere
            top_5_reranked = await reranker_service.rerank_results(query, results, top_n=3)  # Reduced from 5 → 3 for faster context
            
            # 5. Parent-Child Context Expansion (Compression/Deduplication)
            final_context_docs = []
            seen_parent_ids = set()
            
            for child_doc in top_5_reranked:
                parent_id = child_doc.get("metadata", {}).get("parent_id")
                
                if parent_id and parent_id not in seen_parent_ids:
                    # Fetch large parent chunk from Redis
                    parent_data = await redis_client.get_parent_chunk(parent_id)
                    if parent_data:
                        # Happy path: parent chunk found in Redis
                        final_context_docs.append({
                            "id": parent_id,
                            "content": parent_data["content"],
                            "metadata": parent_data["metadata"],
                            "rerank_score": child_doc.get("rerank_score", 0.0)
                        })
                    else:
                        # FIX 1: Redis miss (e.g. container restart wiped parent chunks).
                        # Fall back to the child chunk's own text stored in Pinecone metadata.
                        logger.warning("parent_chunk_redis_miss_using_child_fallback", parent_id=parent_id)
                        child_text = child_doc.get("metadata", {}).get("text", "")
                        final_context_docs.append({
                            "id": child_doc["id"],
                            "content": child_text,
                            "metadata": child_doc.get("metadata", {}),
                            "rerank_score": child_doc.get("rerank_score", 0.0)
                        })
                    seen_parent_ids.add(parent_id)
                elif not parent_id:
                    # Chunk has no parent — use its content directly
                    child_text = child_doc.get("content") or child_doc.get("metadata", {}).get("text", "")
                    final_context_docs.append({**child_doc, "content": child_text})
            
            logger.info("parent_child_expansion_complete", final_docs=len(final_context_docs))

            # FIX 2: Only cache retrieval results if we actually have documents.
            # Caching an empty result would poison the cache for all future identical queries.
            if final_context_docs:
                await semantic_cache.set_retrieval_cache(query, final_context_docs)
                logger.info("retrieval_result_cached", query=query)
            else:
                logger.warning("skipping_cache_empty_retrieval_results", query=query)
            
            return final_context_docs
            
        except Exception as e:
            logger.error("retrieval_failed", error=str(e))
            raise

retrieval_service = HybridRetrievalService()
