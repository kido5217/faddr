"""CLI entry point for database query."""

import argparse
import sys

from rich.table import Table

from faddr import console, logger
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


def pretty_print_result(result):
    """Print data with pretty formatting."""

    table = Table()

    for column_name in result["header"]:
        table.add_column(column_name)

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

    result = database.find_network(cmd_args.get("address"))

    pretty_print_result(result)
