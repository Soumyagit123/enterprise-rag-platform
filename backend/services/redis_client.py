import redis.asyncio as redis
import json
import structlog
import os

logger = structlog.get_logger()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(REDIS_URL, decode_responses=True)

    async def ping(self):
        return await self.client.ping()

    async def store_parent_chunk(self, parent_id: str, content: str, metadata: dict):
        """Store large parent chunks. We'll use this during retrieval to expand context."""
        payload = {
            "content": content,
            "metadata": metadata
        }
        # Parent chunks might not need to expire if they are part of the active index,
        # but for safety/cleanup in a real system we might bound them or sync them with DB.
        await self.client.set(f"parent_chunk:{parent_id}", json.dumps(payload))
        logger.info("parent_chunk_stored", parent_id=parent_id)

    async def get_parent_chunk(self, parent_id: str) -> dict:
        """Retrieve a parent chunk by its ID."""
        data = await self.client.get(f"parent_chunk:{parent_id}")
        if data:
            return json.loads(data)
        return None

redis_client = RedisClient()
