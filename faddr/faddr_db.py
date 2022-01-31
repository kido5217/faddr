"""CLI entry points of faddr."""

import argparse

from faddr import logger
from faddr.rancid import RancidDir
from faddr.settings import load_settings


def parse_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        "-s",
        "--settings-file",
        help="Faddr settings file  location",
    )

    args = parser.parse_args()
    return vars(args)


def cli():
    """Parsing devices' config files and writing data to database."""
    cmd_args = parse_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    settings = load_settings(cmd_args.get("settings_file"))
    logger.debug(f"Generated settings: {settings.dict()}")
