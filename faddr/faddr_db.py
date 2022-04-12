"""CLI entry point for database creation."""

import argparse
import sys

import ray
from pydantic import ValidationError

from faddr import __version__, logger
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
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print version and exit",
    )

    args = parser.parse_args()
    return vars(args)


@ray.remote
def parse_config(config, profile=None, template_dir=None):
    """Parse provided configuration and return structured data."""

    logger.info(f'Parsing \'{config["name"]}\'')

    device = {}

    try:
        parser = Parser(
            config["path"],
            profile=profile,
            template_dir=template_dir,
        )
        device.update(parser.parse())
    except FaddrParserUnknownProfile:
        logger.warning(f"Unsupported content-type in '{config}'")
    except FaddrParserConfigFileAbsent:
        logger.warning(f"Config file absent: '{config}'")
    except FaddrParserConfigFileEmpty:
        logger.warning(f"Config file empty: '{config}'")
    except ValidationError as err:
        logger.warning(f"Failed to postprocess '{config}': {err.json()}")

    device.update(
        {
            "path": str(config["path"]),
            "name": str(config["name"]),
            "source": "rancid",
        }
    )

    return device


@ray.remote
def store_in_db(database, device):
    """Insert device data to database."""
    data_fields = ("interfaces",)
    device_have_data = False
    for data_field in data_fields:
        if len(device[data_field]) > 0:
            device_have_data = True

    if not device_have_data:
        logger.warning(f'Device \'{device["name"]}\' data is empty, skipping')
        return False

    logger.info(f'Inserting \'{device["name"]}\' info DB')
    database.insert_device(device)
    return True


def main():
    """Parsing devices' config files and writing data to database."""

    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    if cmd_args.get("version", False):
        logger.debug("Version was requested. Printing and exiting")
        print(__version__)
        sys.exit(0)

    # Load settings
    logger.info("Loading settings")
    try:
        settings = load_settings(settings_file=cmd_args.get("settings_file"))
    except FaddrSettingsFileFormatError:
        logger.exception("Failed to load settings")
        sys.exit(1)
    logger.debug(f"Generated settings: {settings.dict()}")

    # Connect to database and create new revision
    logger.info("Connecting to database and creating new revision")
    try:
        database = Database(**settings.database.dict())
    except FaddrDatabaseDirError:
        logger.exception("Failed to open database")
        sys.exit(1)
    database.new_revision()

    # Init multiprocessing framework
    logger.info("Initializing multiprocessing framework")
    ray.init(num_cpus=settings.processes, num_gpus=0)
    inserted_ids = []

    skipped_devices = 0

    logger.info("Parsing rancid dirs")
    for rancid_dir in settings.rancid.dirs:
        rancid = RancidDir(rancid_dir.path)
        logger.info(f"Parsing configs in rancid dir '{rancid_dir.path}'")

        for config in rancid.configs:
            if not config.get("is_enabled", False):
                logger.info(
                    f"Config '{config['name']}' is disabled in router.db, skipping"
                )
                skipped_devices += 1
                continue

            # Get profile from dir's mapping.
            # If Absent - get if from global rancid mapping.
            # If it isn't there as well - try using raw content_type
            profile = rancid_dir.mapping.get(
                config["content_type"],
                settings.rancid.mapping.get(
                    config["content_type"], config["content_type"]
                ),
            )
            if profile not in Parser.SUPPORTED_PROFILES:
                logger.warning(f"Unsupported content-type in '{config}'")
                skipped_devices += 1
                continue

            data_id = parse_config.options(name="faddr::parse_config()").remote(
                config,
                profile=profile,
                template_dir=settings.templates_dir,
            )
            inserted_id = store_in_db.options(name="faddr::store_in_db()").remote(
                database, data_id
            )
            inserted_ids.append(inserted_id)

    # All exception handling should be inside @ray.remote functions,
    # so we don't catch any exceptions here
    logger.info("Waiting for parser and database processes to finish")
    result = [ray.get(inserted_id) for inserted_id in inserted_ids]

    # Statistics
    parsed_devices = result.count(True)
    skipped_devices = skipped_devices + result.count(False)
    logger.info(f"Devices parsed and inserted: {parsed_devices}")
    logger.info(f"Devices skipped: {skipped_devices}")

    # Only mark revision as active and remove older revisions
    # if at least one device has been parsed successfully
    if parsed_devices > 0:
        database.set_default()
        logger.info("Deleting old revisions")
        deleted_revions = database.cleanup()
        logger.info(f"Revisions deleted: {deleted_revions}")
