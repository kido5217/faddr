"""CLI entry points of faddr."""

import argparse
import sys

from faddr import logger
from faddr.rancid import RancidDir
from faddr.database import Database


def parse_args_db():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--rancid-path",
        default="/var/lib/rancid",
        help="Rancid basedir location",
    )

    parser.add_argument(
        "-g",
        "--rancid-groups",
        help="Rancid groups to parse, separated bu coma(,)",
    )

    parser.add_argument(
        "-d",
        "--database-file",
        default="/var/db/faddr/faddr.json",
        help="TinyDB file location",
    )

    args = parser.parse_args()
    return vars(args)


def faddr_db():
    """Parsing devices' config files and writing data to database."""
    args = parse_args_db()
    logger.debug(f"Arguments parsed: {args}")

    rancid = RancidDir(args["rancid_path"])

    db = Database(args["database_file"])

    if not rancid.is_valid():
        error = (
            f'"{args["rancid_path"]}" is not a valid rancid BASEDIR '
            "or was not properly initialised with rancid-csv utility"
        )
        logger.error(error)
        sys.exit(1)

    # Get groups list found in rancid's base dir
    groups = rancid.load_groups(args["rancid_groups"])
    logger.debug(f"Found rancid groups: {groups}")

    for group in groups:
        logger.debug(f"Parsing devices in group {group}")
        data = rancid.parse_configs(group)
        if len(data) > 0:
            db.insert(data)
