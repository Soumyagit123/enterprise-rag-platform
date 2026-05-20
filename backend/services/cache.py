import structlog
import json
import hashlib
import struct
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
from .redis_client import redis_client, REDIS_URL
from .embedding import embedding_service

logger = structlog.get_logger()

# TTLs in seconds
EMBEDDING_CACHE_TTL = 7 * 24 * 60 * 60  # 7 days
RETRIEVAL_CACHE_TTL = 1 * 24 * 60 * 60  # 1 day
RESPONSE_CACHE_TTL = 6 * 60 * 60        # 6 hours

class SemanticCacheService:
    def __init__(self):
        self.redis = redis_client.client
        # Instantiate a separate binary-safe connection client (decode_responses=False)
        # to prevent UTF-8 decoding errors when reading raw float vector blobs
        self.redis_bin = redis.from_url(REDIS_URL, decode_responses=False)
        self.index_created = False

    def _hash_query(self, query: str) -> str:
        return hashlib.sha256(query.encode('utf-8')).hexdigest()

    async def _ensure_index(self):
        """
        Dynamically determine vector dimensions and ensure the HNSW index is created in Redis Stack.
        """
        if self.index_created:
            return
        
        try:
            # Dynamically fetch embedding dimension of the current active model
            test_vector = await embedding_service.embeddings.aembed_query("connection check")
            dim = len(test_vector)
            
            # Execute FT.CREATE command to build a HNSW Vector index on hashes prefixed with cache:semantic_response:
            await self.redis_bin.execute_command(
                "FT.CREATE", "idx:semantic_cache",
                "ON", "HASH",
                "PREFIX", "1", "cache:semantic_response:",
                "SCHEMA",
                "query", "TEXT",
                "response", "TEXT",
                "vector", "VECTOR", "HNSW", "6",
                "TYPE", "FLOAT32",
                "DIM", str(dim),
                "DISTANCE_METRIC", "COSINE"
            )
            logger.info("redis_vss_index_created", dimension=dim)
        except Exception as e:
            if "Index already exists" in str(e):
                self.index_created = True
            else:
                logger.error("redis_vss_index_creation_failed", error=str(e))
        self.index_created = True

    async def check_semantic_response_cache(self, query: str) -> Optional[str]:
        """
        Check if we already generated a response for this or a semantically identical query.
        Utilizes KNN Cosine Vector Search.
        """
        await self._ensure_index()
        
        try:
            # Generate and normalize embedding vector for user query
            query_vector = await embedding_service.embeddings.aembed_query(query)
            query_vector = embedding_service.normalize_vector(query_vector)
            
            # Pack float vector into binary float array (FLOAT32 format for Redis VSS compatibility)
            query_vector_blob = struct.pack(f"{len(query_vector)}f", *query_vector)
            
            # Perform K-Nearest Neighbors search to find the single closest match
            res = await self.redis_bin.execute_command(
                "FT.SEARCH", "idx:semantic_cache",
                "*=>[KNN 1 @vector $query_vector AS vector_score]",
                "PARAMS", "2", "query_vector", query_vector_blob,
                "DIALECT", "2"
            )
            
            # If a match is found in the search result
            if res and res[0] > 0:
                fields = res[2]
                fields_dict = {}
                for i in range(0, len(fields), 2):
                    fields_dict[fields[i]] = fields[i+1]
                
                # Cosine distance = 1 - cosine_similarity
                distance = float(fields_dict.get(b"vector_score", b"1.0").decode("utf-8"))
                similarity = 1.0 - distance
                
                # Threshold for semantic match (e.g. 88% similarity)
                SIMILARITY_THRESHOLD = 0.88
                
                if similarity >= SIMILARITY_THRESHOLD:
                    cached_response = fields_dict.get(b"response", b"").decode("utf-8")
                    logger.info("semantic_cache_hit", query=query, similarity=similarity)
                    return cached_response
                else:
                    logger.info("semantic_cache_miss_low_similarity", query=query, similarity=similarity)
        except Exception as e:
            logger.error("semantic_cache_lookup_failed", error=str(e))

        # Resilient fallback: Check standard SHA-256 exact match query cache
        key = f"cache:response:{self._hash_query(query)}"
        data = await self.redis.get(key)
        if data:
            logger.info("cache_hit_response_fallback", query=query)
            return data
        return None

    async def set_semantic_response_cache(self, query: str, response: str):
        """
        Store a newly generated response in both the Vector Index cache and the exact match fallback cache.
        """
        await self._ensure_index()
        
        try:
            # Generate and normalize embedding vector
            query_vector = await embedding_service.embeddings.aembed_query(query)
            query_vector = embedding_service.normalize_vector(query_vector)
            
            # Pack float vector into binary float array
            query_vector_blob = struct.pack(f"{len(query_vector)}f", *query_vector)
            
            # Write key hash directly with raw vector bytes
            key = f"cache:semantic_response:{self._hash_query(query)}"
            await self.redis_bin.hset(key, mapping={
                "query": query,
                "response": response,
                "vector": query_vector_blob
            })
            await self.redis_bin.expire(key, RESPONSE_CACHE_TTL)
            logger.info("semantic_cache_set", query=query, ttl=RESPONSE_CACHE_TTL)
        except Exception as e:
            logger.error("semantic_cache_store_failed", error=str(e))

        # Resilient fallback: Write to standard SHA-256 exact match cache key
        fallback_key = f"cache:response:{self._hash_query(query)}"
        await self.redis.setex(fallback_key, RESPONSE_CACHE_TTL, response)

    async def check_retrieval_cache(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Check if we have cached retrieval results for this query.
        """
        key = f"cache:retrieval:{self._hash_query(query)}"
        data = await self.redis.get(key)
        if data:
            logger.info("cache_hit_retrieval", query=query)
            return json.loads(data)
        return None

    async def set_retrieval_cache(self, query: str, docs: List[Dict[str, Any]]):
        key = f"cache:retrieval:{self._hash_query(query)}"
        await self.redis.setex(key, RETRIEVAL_CACHE_TTL, json.dumps(docs))
        logger.info("cache_set_retrieval", query=query, ttl=RETRIEVAL_CACHE_TTL)

    async def check_embedding_cache(self, text: str) -> Optional[List[float]]:
        """
        Check if we already embedded this exact chunk of text.
        """
        key = f"cache:embedding:{self._hash_query(text)}"
        data = await self.redis.get(key)
        if data:
            logger.info("cache_hit_embedding")
            return json.loads(data)
        return None

    async def set_embedding_cache(self, text: str, vector: List[float]):
        key = f"cache:embedding:{self._hash_query(text)}"
        await self.redis.setex(key, EMBEDDING_CACHE_TTL, json.dumps(vector))
        logger.info("cache_set_embedding", ttl=EMBEDDING_CACHE_TTL)

semantic_cache = SemanticCacheService()
