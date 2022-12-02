"""Configure logging for faddr."""

import sys

from loguru import logger

from faddr.settings import FaddrSettings

settings = FaddrSettings()

# Update logging level from settings
logger.remove()
logger.add(sys.stdout, level=settings.log_level)
