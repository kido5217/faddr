"""CLI entry point for database query."""

import argparse
import json
import sys

from rich import box
from rich.console import Console
from rich.table import Table

from faddr import __version__
from faddr.database import Database
from faddr.logging import logger
from faddr.results import NetworkResult
from faddr.settings import FaddrSettings


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


def make_table(result, row_type, include_description=True, color=True, border=False):
    """Create rich table according to search results and cli arguments."""

    if border:
        table_border = box.SQUARE
        padding = (0, 1, 0, 1)
    else:
        table_border = None
        padding = (0, 2, 0, 0)

    table = Table(
        title=row_type.capitalize(),
        highlight=color,
        header_style=None,
        box=table_border,
        safe_box=True,
        padding=padding,
    )

    keys = []

    # Prepare header according to passed cli options
    header = []
    header[:] = result.schema["headers"][row_type]
    if not include_description and row_type == "direct":
        header.remove("Description")
    if len(result.data.keys()) == 1:
        header.remove("Query")
    for column in header:
        table.add_column(column)

    # Filter keys according to passed cli options
    keys[:] = result.schema["keys"][row_type]
    if not include_description and row_type == "direct":
        keys.remove("description")
    if len(result.data.keys()) == 1:
        keys.remove("query")

    return table, keys


def print_result(
    result, include_description=True, output_format="table", color=True, border=False
):
    """Print result to console."""

    console = Console()
    if output_format == "json":
        console.print(json.dumps(result.data, indent=2))
    elif output_format == "table":
        # Dont try to process empty results
        if len(result.data.keys()) < 1:
            return

        tables = {}
        keys = {}

        # Append data to tables
        for query in result.data.keys():
            for row_data in result.data[query]:
                row_type = row_data["type"]

                # Create rich table if it doesn't exist
                if row_type not in tables:
                    tables[row_type], keys[row_type] = make_table(
                        result, row_type, include_description, color, border
                    )

                # Add rows to table
                row_keys = keys[row_type]
                if "query" in row_keys:
                    row_data["query"] = query

                # Normalize cell data
                # cells = [str(row_data.get(key)) for key in row_keys]
                cells = []
                for key in row_keys:
                    value = row_data.get(key)
                    if value is None or value is False:
                        cells.append("-")
                    elif isinstance(value, bool) and value:
                        cells.append("[bold red]Yes")
                    else:
                        cells.append(str(value))

                tables[row_data["type"]].add_row(*cells)

        # Print tables
        table_order = ("direct", "static")
        console.print()
        for table in table_order:
            if table in tables:
                console.print(tables[table])
                console.print()


def main():
    """Query database"""

    # Load settings
    settings = FaddrSettings()
    logger.debug(f"Generated settings: {settings.dict()}")

    # Parse CMD
    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    if cmd_args.get("version", False):
        logger.debug("Version was requested. Printing and exiting")
        print(__version__)
        sys.exit(0)

    database = Database(**settings.database.dict())

    result = NetworkResult(
        database.find_networks(
            cmd_args.get("ip_address"), network_types=("direct", "static")
        )
    )

    print_result(
        result,
        include_description=cmd_args.get("description"),
        output_format=cmd_args.get("output"),
        color=cmd_args.get("color"),
        border=cmd_args.get("table"),
    )
