"""CLI entry points of faddr."""

import argparse

from faddr import logger
from faddr.rancid import RancidDir
from faddr.config import load_settings


def parse_args_db():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

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
    logger.debug(f"Arguments from CMD: {args}")
    settings = load_settings()

    logger.debug(f"Loaded settings: {settings.__dict__}")
