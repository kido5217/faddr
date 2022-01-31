"""CLI entry points of faddr."""

import argparse
import sys

from faddr import logger
from faddr.rancid import RancidDir
from faddr.settings import load_settings
from faddr.exceptions import FaddrSettingsFileFormatError


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

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError:
        logger.info(f"Failed to load settings from {cmd_args.get('settings_file')}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")
