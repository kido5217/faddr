"""Parse network devices' configuration and store in database."""

import os
import sys

from loguru import logger
from rich.console import Console

__version__ = "0.4.0-alpha.1"

# Setup rich console for pretty printing
console = Console()
