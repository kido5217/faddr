"""Init default configuration and read configuration from file."""

import copy
import pathlib

import yaml

from pydantic import BaseModel

from faddr import logger


DEFAULT_CONFIG = {
    "database": {
        "database_type": "tynidb",
        "database_dir": "/var/db/faddr/",
        "database_file": "faddr.json",
    },
    "rancid": {
        "rancid_dir": "/var/lib/rancid/",
    },
}

DEFAULT_SYSTEM_CONFIG_PATH = "/etc/faddr/faddr.yaml"


def load_config_from_file(config_path):
    """Read config file."""
    config = {}
    config_file = pathlib.Path(config_path)
    if config_file.exists():
        try:
            with open(config_file, mode="r", encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
        except Exception:
            logger.exception(f"Caught exception while loading {config_path}")
    else:
        logger.warning(f"Configuration file {config_file} doesn't exist.")

    return config


def parse_cmd_args(cmd_args):
    """Parse arguments from cmd and return FaddrConfig-compatible dict."""
    config = load_config_from_file(DEFAULT_SYSTEM_CONFIG_PATH)

    if cmd_args.get("confguration_file") is not None:
        system_config = load_config_from_file(cmd_args.get("confguration_file"))
        config.update(system_config)

    if cmd_args.get("rancid_dir") is not None:
        config["rancid"]["rancid_dir"] = cmd_args.get("rancid_dir")

    if cmd_args.get("database_dir") is not None:
        config["database"]["database_dir"] = cmd_args.get("database_dir")

    if cmd_args.get("database_file") is not None:
        config["database"]["database_file"] = cmd_args.get("database_file")

    return config


class Database(BaseModel):
    """Datavase type, location, credentials etc."""

    database_type: str
    database_dir: str
    database_file: str


class Rancid(BaseModel):
    """Racnid dir location, profile mapping etc."""

    rancid_dir: str = None
    profile_mapping: dict = {}


class FaddrConfig(BaseModel):
    """Faddr configuration."""

    database: Database
    rancid: Rancid


def load_config(cmd_args):
    """Dummy class for config init with default values."""

    logger.debug(f"Default config: {DEFAULT_CONFIG}")

    if cmd_args is not None:
        logger.debug(f"CMD arguments: {cmd_args}")
        new_config = parse_cmd_args(cmd_args)
    else:
        new_config = load_config_from_file(DEFAULT_SYSTEM_CONFIG_PATH)
    logger.debug(f"Generated config: {new_config}")

    class_obj = FaddrConfig(**new_config)
    return class_obj
