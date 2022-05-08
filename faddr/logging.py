"""Configure logging for faddr."""

import sys

from loguru import logger

from faddr.settings import FaddrSettings

settings = FaddrSettings()

# Update logging level from settings
logger.remove()
if settings.debug:
    logger.add(sys.stdout, level="DEBUG")
else:
    logger.add(sys.stdout, level="INFO")
