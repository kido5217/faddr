"""Classes for de/serializing and printing search results."""

import json

from rich import box
from rich.table import Table

from faddr import console


class NetworkResult:
    """Process network search results."""

    schema = {
        "headers": {
            "direct": (
                "Query",
                "Device",
                "Interface",
                "IP",
                "VRF",
                "ACL in",
                "ACL out",
                "Shutdown",
                "Description",
            ),
        },
        "keys": {
            "direct": (
                "query",
                "device",
                "interface",
                "ip_address",
                "vrf",
                "acl_in",
                "acl_out",
                "is_disabled",
                "description",
            )
        },
        "tables": ("direct",),
    }

    def __init__(self, data):
        self.data = data
        self.tables = None

    def print(
        self,
        output="table",
        include_description=False,
        color=False,
        border=False,
    ):
        """Print data to stdout."""
        if output == "table":
            if self.tables is None:
                self._make_tables(
                    include_description=include_description, color=color, border=border
                )

            for table in self.schema["tables"]:
                if table in self.tables:
                    console.print(self.tables[table])
        elif output == "json":
            console.print(json.dumps(self.data, indent=2))

    @staticmethod
    def format_row(row, keys):
        """Create list from dict."""
        cells = []
        for key in keys:
            value = row.get(key)
            if value is None or value is False:
                cells.append("-")
            elif isinstance(value, bool) and value:
                cells.append("[bold red]Yes")
            else:
                cells.append(str(value))
        return cells

    def _make_tables(self, include_description=False, color=False, border=False):
        tables = {}
        if border:
            table_border = box.SQUARE
            padding = (0, 1, 0, 1)
        else:
            table_border = None
            padding = (0, 2, 0, 0)

        for query, rows in self.data.items():
            for row in rows:
                table = row.pop("type")
                if table not in self.schema["tables"]:
                    continue

                if len(self.data) > 1:
                    row["query"] = query
                    start_offset = 0
                else:
                    start_offset = 1

                if include_description:
                    end_offset = None
                else:
                    end_offset = -1

                # Create new table
                if table not in tables:
                    tables[table] = Table(
                        expand=False,
                        highlight=color,
                        header_style=None,
                        box=table_border,
                        safe_box=True,
                        padding=padding,
                    )

                    # Add header
                    for column_name in self.schema["headers"][table][
                        start_offset:end_offset
                    ]:
                        tables[table].add_column(
                            column_name,
                            overflow=None,
                        )

                # Add row to table
                keys = self.schema["keys"][table][start_offset:end_offset]
                tables[table].add_row(*self.format_row(row, keys))

        self.tables = tables
