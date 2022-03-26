"""CLI entry point for database creation."""

import argparse
import sys

from faddr import logger
from faddr.database import Database
from faddr.exceptions import (
    FaddrDatabaseDirError,
    FaddrParserConfigFileAbsent,
    FaddrParserConfigFileEmpty,
    FaddrParserUnknownProfile,
    FaddrSettingsFileFormatError,
)
from faddr.parser import Parser
from faddr.rancid import RancidDir
from faddr.settings import load_settings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        "-D",
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


def parse_config(config, profile=None, template_dir=None):
    """Parse provided configuration and return structured data."""
    device = {}

    try:
        parser = Parser(
            config,
            profile=profile,
            template_dir=template_dir,
        )
        data = parser.parse()
        device.update(data)
        device_stats = {}
        for category, category_data in data.items():
            device_stats[category] = len(category_data)
        logger.info(f"Parsed: {device_stats}")
    except FaddrParserUnknownProfile:
        logger.warning(f"Unsupported config: {config}")
    except FaddrParserConfigFileAbsent:
        logger.warning(f"Config file absent: {config}")
    except FaddrParserConfigFileEmpty:
        logger.warning(f"Config file empty: {config}")

    return device


def main():
    """Parsing devices' config files and writing data to database."""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError as err:
        logger.error(f"Failed to load settings: {err}")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    try:
        database = Database(**settings.database.dict())
    except FaddrDatabaseDirError as err:
        logger.error(f"Failed to open database: {err}")
        sys.exit(1)
    database.new_revision()

    for rancid_dir in settings.rancid.dirs:
        rancid = RancidDir(rancid_dir.path)
        logger.info(f"Parsing configs in rancid dir '{rancid_dir.path}'")

        for config in rancid.configs:
            if not config.get("is_enabled", False):
                logger.info(
                    f"Config '{config['name']}' is disabled in router.db, skipping"
                )
                continue

            logger.info(f'Parsing \'{config["name"]}\' from \'{config["path"]}\'')
            device = parse_config(
                config["path"],
                rancid_dir.mapping.get(
                    config["content_type"],
                    settings.rancid.mapping.get(config["content_type"]),
                ),
                settings.templates_dir,
            )
            if len(device) > 0:
                device_info = {
                    "path": str(config["path"]),
                    "name": str(config["name"]),
                    "source": "rancid",
                }
                device["info"] = device_info
                database.insert_device(device)

    database.set_default()
    database.cleanup()
