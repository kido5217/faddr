"""CLI entry point for database query."""

import argparse
import sys

from faddr import __version__, console, logger
from faddr.database import Database
from faddr.exceptions import FaddrSettingsFileFormatError
from faddr.results import NetworkResult
from faddr.settings import load_settings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ip_address",
        nargs="*",
        help="IP address to search",
    )
    parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        help="Enable color printing",
    )
    parser.add_argument(
        "-D",
        "--debug",
        action="store_true",
        help="Enable debug messages",
    )
    parser.add_argument(
        "-d",
        "--description",
        action="store_true",
        help="Print description column",
    )

    parser.add_argument(
        "-o",
        "--output",
        choices=("table", "json"),
        default="table",
        help="Output format, default is 'table'",
    )
    parser.add_argument(
        "-s",
        "--settings-file",
        help="Faddr settings file  location",
    )
    parser.add_argument(
        "-t",
        "--table",
        action="store_true",
        help="Print table borders",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print version and exit",
    )

    args = parser.parse_args()
    return vars(args)


def parse_input(input_data):
    """Remove masks from input ip addresses."""
    query = []
    for address in input_data:
        query.append(address.split("/")[0])
    return query


def main():
    """Query database"""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    if cmd_args.get("version", False):
        logger.debug("Version was requested. Printing and exiting")
        print(__version__)
        sys.exit(0)

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        console.print(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    database = Database(**settings.database.dict())

    result = NetworkResult(database.find_networks(cmd_args.get("ip_address")))
    result.print(
        include_description=cmd_args.get("description"),
        output=cmd_args.get("output"),
        color=cmd_args.get("color"),
        border=cmd_args.get("table"),
    )
