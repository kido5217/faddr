"""CLI entry point for database query."""

import argparse
import sys

from rich import box
from rich.table import Table

from faddr import console, logger
from faddr.database import Database
from faddr.exceptions import FaddrSettingsFileFormatError
from faddr.settings import load_settings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ip_address",
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

    args = parser.parse_args()
    return vars(args)


def pretty_print_result(result, print_description=False, color=False):
    """Print data with pretty formatting."""

    if print_description is False:
        result["header"].remove("Description")

    table = Table(
        expand=True,
        highlight=color,
        header_style=None,
        box=box.SQUARE,
    )

    for column_name in result["header"]:
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

        table.add_row(*[str(row.get(cell_name, "-")) for cell_name in result["header"]])

    console.print(table)


def main():
    """Query database"""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        console.print(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    database = Database(**settings.database.dict())

    result = database.find_network(cmd_args.get("ip_address"))

    pretty_print_result(
        result,
        print_description=cmd_args.get("description", False),
        color=cmd_args.get("color", False),
    )
