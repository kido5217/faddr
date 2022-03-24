"""Parse network devices' configuration and store in database."""

import os
import sys

from loguru import logger
from rich.console import Console

__version__ = "0.0.12"

if os.getenv("FADDR_DEBUG") or any(arg in sys.argv for arg in ("-D", "--debug")):
    LOG_LEVEL = "DEBUG"
else:
    LOG_LEVEL = "INFO"

logger.remove()
logger.add(sys.stdout, level=LOG_LEVEL)

# Setup rich console for pretty printing
console = Console()
