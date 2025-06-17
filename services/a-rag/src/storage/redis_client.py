"""
file: services/a-rag/src/storage/redis_client.py

Module for managing the connection to the Redis cache.
Provides a singleton Redis client instance for the application.
"""

import redis.asyncio as aioredis

from core.config import settings

# Create a single, reusable Redis client instance.
# This pattern is efficient as it maintains a connection pool.
redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True,  # Automatically decode responses from bytes to strings
)

print("Redis client initialized.")
