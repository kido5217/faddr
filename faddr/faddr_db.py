"""CLI entry point for database creation."""

import argparse
import sys

import ray
from pydantic import ValidationError

from faddr import __version__
from faddr.database import Database
from faddr.exceptions import (
    FaddrDatabaseDirError,
    FaddrDatabaseMultipleRevisionsActive,
    FaddrParserConfigFileAbsent,
    FaddrParserConfigFileEmpty,
    FaddrParserUnknownProfile,
    FaddrRepoPathError,
)
from faddr.logging import logger
from faddr.parser import Parser
from faddr.repo import RepoList
from faddr.settings import FaddrSettings


def parse_cmd_args():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        "action",
        type=str,
        choices=("init", "parse"),
        help="Action to perform",
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
def parse_config(config, template_dir=None):
    """Parse provided configuration and return structured data."""

    logger.info(f"Parsing '{config}'")

    device = {}

    try:
        parser = Parser(
            config.path,
            profile=config.profile,
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
            "path": str(config.path),
            "name": config.name,
            "source": config.source,
        }
    )

    return device


@ray.remote
def store_in_db(database, device):
    """Insert device data to database."""
    data_fields = ("interfaces",)
    device_have_data = False
    for data_field in data_fields:
        if len(device.get(data_field, [])) > 0:
            device_have_data = True

    if not device_have_data:
        logger.warning(f'Device \'{device["name"]}\' data is empty, skipping')
        return False

    logger.info(f'Inserting \'{device["name"]}\' into DB')
    database.insert_device(device)
    return True


def main():
    """Parsing devices' config files and writing data to database."""

    # Load settings
    settings = FaddrSettings()
    logger.debug(f"Loaded settings: {settings.dict()}")

    # Parse CMD args
    cmd_args = parse_cmd_args()
    logger.debug(f"Arguments from CMD: {cmd_args}")

    if cmd_args.get("version", False):
        logger.debug("Version was requested. Printing and exiting")
        print(__version__)
        sys.exit(0)

    if cmd_args.get("action") == "parse":
        parse(settings)
    elif cmd_args.get("action") == "init":
        init(settings)


def init(settings):
    """Init new database."""

    # Connect to database and create tables
    logger.info("Connecting to database and creating tables")
    try:
        Database(init=True, **settings.database.dict())
    except FaddrDatabaseDirError:
        logger.exception("Failed to open database")
        sys.exit(1)


def parse(settings):
    """Parse configs and store them in database."""

    # Create repo list here
    repo_list = RepoList(mapping=settings.mapping)
    try:
        repo_list.parse_file(settings.repo_file)
    except FaddrRepoPathError:
        logger.exception("Failed to parse repo file.")
        sys.exit(1)

    # Connect to database and create new revision
    logger.info("Connecting to database and creating new revision")
    try:
        database = Database(**settings.database.dict()).new_revision()
    except FaddrDatabaseDirError:
        logger.exception("Failed to open database")
        sys.exit(1)
    except FaddrDatabaseMultipleRevisionsActive:
        logger.exception("More than one revision is marked as active")
        sys.exit(1)

    # Init multiprocessing framework
    logger.info("Initializing multiprocessing framework")
    ray.init(num_cpus=settings.processes, num_gpus=0)
    inserted_ids = []

    skipped_devices = 0

    logger.info("Parsing configs")
    for config in repo_list.configs:
        if config.profile not in Parser.SUPPORTED_PROFILES:
            logger.warning(f"Unsupported profile in '{config}'")
            skipped_devices += 1
            continue

        data_id = parse_config.options(name="faddr::parse_config()").remote(
            config,
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
        database.set_active_revision()
        logger.info("Deleting old revisions")
        deleted_revions = database.cleanup()
        logger.info(f"Revisions deleted: {deleted_revions}")
