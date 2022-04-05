"""CLI entry point for database query."""

import argparse
import sys

from rich import box
from rich.table import Table

from faddr import __version__, console, logger
from faddr.database import Database
from faddr.exceptions import FaddrSettingsFileFormatError
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


def pretty_print_result(
    result,
    description=False,
    color=False,
    table=False,
    query_number=1,
):
    """Print data with pretty formatting."""

    header = result["headers"]["full"].copy()
    if description is False:
        header.remove("Description")
    if query_number == 1:
        header.remove("Query")

    table = Table(
        expand=table,
        highlight=color,
        header_style=None,
        box=box.SQUARE if table else None,
        safe_box=True,
        padding=(0, 1, 0, 1) if table else (0, 2, 0, 0),
    )

    for column_name in header:
        table.add_column(
            column_name,
            overflow=None,
        )

    for row in result["data"]:
        # Fix bool and None values.
        for key, value in row.items():
            if value is None:
                row[key] = "-"
            elif isinstance(value, bool) and value:
                row[key] = "[bold red]Yes"
            elif isinstance(value, bool) and not value:
                row[key] = "-"

        table.add_row(*[str(row.get(cell_name, "-")) for cell_name in header])

    console.print(table)


def main():
    """Query database"""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    if cmd_args.get("version", False):
        logger.debug("Version was requested. Printing and exiting")
        print(__version__)
        sys.exit(0)

    query = parse_input(cmd_args.get("ip_address"))

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        console.print(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    database = Database(**settings.database.dict())

    result = database.find_networks(query)

    pretty_print_result(
        result,
        description=cmd_args.get("description", False),
        color=cmd_args.get("color", False),
        table=cmd_args.get("table", False),
        query_number=len(query),
    )
