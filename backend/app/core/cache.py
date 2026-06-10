import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings

# Initialize Redis client using connection pooling
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: str, expire_seconds: int = 3600) -> bool:
    """Set a string value in Redis cache with an expiration time."""
    try:
        await redis_client.set(key, value, ex=expire_seconds)
        return True
    except Exception:
        # Silently fail in production or log it (could configure fallback)
        return False

async def get_cache(key: str) -> Optional[str]:
    """Retrieve a string value from Redis cache."""
    try:
        return await redis_client.get(key)
    except Exception:
        return None

async def delete_cache(key: str) -> bool:
    """Delete a key from Redis cache."""
    try:
        await redis_client.delete(key)
        return True
    except Exception:
        return False

async def set_json_cache(key: str, data: Any, expire_seconds: int = 3600) -> bool:
    """Serialize and store complex data structures in Redis cache as JSON."""
    try:
        serialized_data = json.dumps(data)
        return await set_cache(key, serialized_data, expire_seconds)
    except Exception:
        return False

async def get_json_cache(key: str) -> Optional[Any]:
    """Retrieve and deserialize a JSON data structure from Redis cache."""
    try:
        data = await get_cache(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None

async def clear_cache_pattern(pattern: str) -> bool:
    """Clear all keys matching a specific pattern."""
    try:
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
        return True
    except Exception:
        return False
