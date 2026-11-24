"""Worker entry point: `python -m app.worker`.

The real queue consumer belongs to the transcription module. Until it lands
this keeps the container alive so `docker compose up` stays green.
"""

import asyncio
import logging

from app.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)

IDLE_SECONDS = 30


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("worker started (queue=%s)", settings.redis_url)
    logger.warning("no tasks registered yet - idling")

    while True:
        await asyncio.sleep(IDLE_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("worker stopped")
