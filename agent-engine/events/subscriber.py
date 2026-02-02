import os
import json
import asyncio
import logging

import redis.asyncio as aioredis

logger = logging.getLogger("defai.events.subscriber")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

CHANNELS = [
    "agent.created",
    "agent.started",
    "agent.stopped",
    "agent.paused",
]


async def handle_event(channel: str, data: dict):
    """Process an incoming event. Extend this with real handlers."""
    logger.info(f"Received event on '{channel}': {json.dumps(data)}")

    if channel == "agent.started":
        agent_id = data.get("data", {}).get("agent_id")
        logger.info(f"Agent {agent_id} started — would activate in agent manager")
    elif channel == "agent.stopped":
        agent_id = data.get("data", {}).get("agent_id")
        logger.info(f"Agent {agent_id} stopped — would deactivate in agent manager")


async def run_subscriber():
    """Subscribe to Redis channels and dispatch events."""
    while True:
        try:
            r = aioredis.from_url(REDIS_URL, decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe(*CHANNELS)
            logger.info(f"Subscribed to Redis channels: {CHANNELS}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await handle_event(message["channel"], data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in event: {message['data']}")
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)
