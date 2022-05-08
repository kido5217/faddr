"""Configure logging for faddr."""

import sys
from loguru import logger

from faddr.settings import FaddrSettings

# Update logging level from settings
try:
    settings = FaddrSettings()
except Exception as err:
    logger.exception(f"Failed to load settings: {err}")
else:
    # Config logging
    logger.remove()
    if settings.debug:
        logger.add(sys.stdout, level="DEBUG")
    else:
        logger.add(sys.stdout, level="INFO")
