"""CLI entry point for database query."""

import argparse
import sys

from rich import inspect
from rich.console import Console

from faddr import logger
from faddr.database import Database
from faddr.exceptions import FaddrSettingsFileFormatError
from faddr.settings import load_settings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "address",
        help="Address to search",
    )

    parser.add_argument(
        "-s",
        "--settings-file",
        help="Faddr settings file  location",
    )

    args = parser.parse_args()
    return vars(args)


def main():
    """Query database"""

    # Setup rich console for pretty printing
    console = Console()

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        console.print(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    database = Database(**settings.database.dict())

    result = database.find_network(cmd_args.get("address"))
    console.print(result)
