"""CLI entry point for database creation."""

import argparse
import sys

from faddr import console, logger
from faddr.database import Database
from faddr.exceptions import FaddrParserUnknownProfile, FaddrSettingsFileFormatError
from faddr.parser import Parser
from faddr.rancid import RancidDir, RancidGroup
from faddr.settings import load_settings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug messages",
    )
    parser.add_argument(
        "-s",
        "--settings-file",
        help="Faddr settings file  location",
    )

    args = parser.parse_args()
    return vars(args)


def main():
    """Parsing devices' config files and writing data to database."""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        logger.info(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    database = Database(**settings.database.dict())
    database.new()

    for rancid_dir in settings.rancid.dirs:
        if rancid_dir.kind == "dir":
            rancid = RancidDir(rancid_dir.path)
        elif rancid_dir.kind in ("group", "repo"):
            rancid = RancidGroup(rancid_dir.path)
        else:
            continue

        for config in rancid.configs:
            try:
                parser = Parser(
                    config["path"],
                    rancid_dir.mapping.get(config["content_type"]),
                    settings.templates_dir,
                )
                data = parser.parse()
                device = {
                    "info": {
                        "path": str(config["path"]),
                        "name": str(config["name"]),
                        "source": "rancid",
                    }
                }
                device.update(data)
                database.insert_device(device)
                console.print(device)
            except FaddrParserUnknownProfile:
                logger.debug(f"Unsupported config: {config}")

    database.set_default()
