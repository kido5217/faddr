"""CLI entry points of faddr."""

import argparse
import pathlib
import sys

from faddr import logger
from faddr.config import LoadConfig
from faddr.rancid import RancidDir
from faddr.database import Database


def parse_args_db():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser()

    # TODO: Replave hardcoded unix-like path with OS-independent.
    parser.add_argument(
        "-c",
        "--confguration-file",
        help="Faddr file configuration location",
    )
    parser.add_argument(
        "-r",
        "--rancid-dir",
        help="Rancid basedir location",
    )

    parser.add_argument(
        "-g",
        "--rancid-groups",
        help="Rancid groups to parse, separated by coma(,)",
    )

    parser.add_argument(
        "-d",
        "--database-dir",
        help="Database dir location",
    )

    parser.add_argument(
        "-f",
        "--database-file",
        help="Database file name",
    )

    args = parser.parse_args()
    return vars(args)


def faddr_db():
    """Parsing devices' config files and writing data to database."""
    args = parse_args_db()
    logger.debug(f"Arguments parsed: {args}")

    config = LoadConfig(cmd_args=args)
    print(config.rancid)

    rancid = RancidDir(config.rancid.rancid_dir)

    db = Database(
        pathlib.Path(config.database.database_dir / config.database.database_file)
    )

    if not rancid.is_valid():
        error = (
            f'"{config.rancid.rancid_dir}" is not a valid rancid BASEDIR '
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
