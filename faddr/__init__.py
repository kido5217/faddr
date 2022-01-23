"""Parse network devices' configuration and store in database."""

import sys
import os

from loguru import logger

from faddr.rancid import RancidDir, RancidGroup


__version__ = "0.0.4"
__all__ = (
    "RancidDir",
    "RancidGroup",
)

if os.getenv("FADDR_DEBUG"):
    LOG_LEVEL = "DEBUG"
else:
    LOG_LEVEL = "INFO"

logger.remove()
logger.add(sys.stdout, level=LOG_LEVEL)
