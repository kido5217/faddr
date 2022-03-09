"""CLI entry point for database creation."""

import argparse
import sys

from faddr import logger
from faddr.database import Database
from faddr.exceptions import (
    FaddrParserConfigFileAbsent,
    FaddrParserUnknownProfile,
    FaddrSettingsFileFormatError,
)
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
        logger.info(f"Parsing configs in rancid dir '{rancid_dir.path}'")

        for config in rancid.configs:
            logger.info(f'Parsing \'{config["name"]}\' from \'{config["path"]}\'')
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
                device_stats = {}
                for category, category_data in data.items():
                    if category != "info":
                        device_stats[category] = len(category_data)
                logger.info(
                    f'Inserted device \'{device["info"]["name"]}\' data into database'
                )
                logger.info(f'\'{device["info"]["name"]}\' stats: {device_stats}')
            except FaddrParserUnknownProfile:
                logger.warning(f"Unsupported config: {config}")
            except FaddrParserConfigFileAbsent:
                logger.warning(f"Config file absent: {config}")

    database.set_default()
