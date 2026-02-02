import os
import json
import logging
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger("defai.events")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


async def publish_event(channel: str, data: dict[str, Any]):
    """Publish an event to a Redis channel."""
    try:
        r = await get_redis()
        message = json.dumps({
            "event": channel,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await r.publish(channel, message)
        logger.info(f"Published event: {channel}", extra={"data": data})
    except Exception as e:
        logger.warning(f"Failed to publish event {channel}: {e}")
