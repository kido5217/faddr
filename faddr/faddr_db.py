"""CLI entry point for database creation."""

import argparse
import sys

import ray

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


@ray.remote
def parse_config(config, profile=None, template_dir=None):
    """Parse provided configuration and return structured data."""
    device = {
        "info": {
            "path": str(config["path"]),
            "name": str(config["name"]),
            "source": "rancid",
        }
    }
    try:
        parser = Parser(
            config["path"],
            profile=profile,
            template_dir=template_dir,
        )
        data = parser.parse()
        device.update(data)
    except FaddrParserUnknownProfile:
        logger.warning(f"Unsupported content-type '{profile}' in '{config}'")
    except FaddrParserConfigFileAbsent:
        logger.warning(f"Config file absent: '{config}'")
    except FaddrParserConfigFileEmpty:
        logger.warning(f"Config file empty: '{config}'")
    return device


def main():
    """Parsing devices' config files and writing data to database."""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    # Load settings
    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError:
        logger.exception("Failed to load settings")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    # Connect to database and create new revision
    try:
        database = Database(**settings.database.dict())
    except FaddrDatabaseDirError:
        logger.exception("Failed to open database")
        sys.exit(1)
    database.new_revision()

    # Init multiprocessing framework
    ray.init(num_cpus=settings.processes, num_gpus=0)
    data_ids = []

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
            profile = rancid_dir.mapping.get(
                config["content_type"],
                settings.rancid.mapping.get(config["content_type"]),
            )
            device = parse_config.remote(
                config,
                profile=profile,
                template_dir=settings.templates_dir,
            )
            data_ids.append(device)

    # All exception handling should be inside parse_config function,
    # so we don't catch any exceptions here
    logger.info("Waiting for parser processes to finish...")
    devices = ray.get(data_ids)
    logger.info(f"Devices parsed: {len(devices)}")

    if len(devices) > 0:
        for device in devices:
            logger.info(f'Inserting {device["info"]["name"]} info DB...')
            database.insert_device(device)
        logger.info(f"Devices inserted: {len(devices)}")

        # Only mark revision as active and remove older revions
        # if at least one device has been parsed successfully
        database.set_default()
        logger.info("Deleting old revisions...")
        deleted_revions = database.cleanup()
        logger.info(f"Revisions deleted: {deleted_revions}")
