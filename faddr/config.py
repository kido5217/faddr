"""Init default configuration and read configuration from file."""

import copy
import os
import pathlib

import yaml

from pydantic import BaseModel

from faddr import logger


DEFAULT_CONFIG = {
    "database": {
        "dir": "/var/db/faddr/",
        "file": "faddr.json",
    },
    "rancid": {
        "dir": "/var/lib/rancid/",
    },
}

DEFAULT_SYSTEM_CONFIG_PATH = "/etc/faddr/faddr.yaml"


class Database(BaseModel):
    """Datavase type, location, credentials etc."""

    dir: str
    file: str


class Rancid(BaseModel):
    """Racnid dir location, profile mapping etc."""

    dir: str = None
    profile_mapping: dict = {}


class FaddrConfig(BaseModel):
    """Faddr configuration."""

    database: Database
    rancid: Rancid


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


def load_config_from_variables(variables):
    """Parse FADDR_* enviroment variables and return FaddrConfig-compatible dict."""
    config = {}

    for var in variables:
        if var.startswith("FADDR_") and var != "FADDR_DEBUG":
            var_string = str(var)[6:].casefold()
            var_list = var_string.split("_")
            var_value = variables[var]
            if len(var_list) == 2:
                if var_list[0] in config:
                    config[var_list[0]][var_list[1]] = var_value
                else:
                    config[var_list[0]] = {var_list[1]: var_value}
            else:
                logger.warning(
                    f'Unrecognized variable "{var}" with value "{variables[var]}"'
                )

    return config


def load_config_from_enviroment_cmd(cmd_args):
    """Parse arguments from cmd and return FaddrConfig-compatible dict."""
    config = {}

    if cmd_args.get("rancid_dir") is not None:
        config["rancid"]["rancid_dir"] = cmd_args.get("rancid_dir")

    if cmd_args.get("database_dir") is not None:
        config["database"]["database_dir"] = cmd_args.get("database_dir")

    if cmd_args.get("database_file") is not None:
        config["database"]["database_file"] = cmd_args.get("database_file")

    return config


def load_config(cmd_args=None, system_config_path=DEFAULT_SYSTEM_CONFIG_PATH):
    """Load config from all available sources and generate FaddrConfig object."""

    if isinstance(cmd_args, dict):
        if cmd_args.get("confguration_file") is not None:
            system_config_path = cmd_args.get("confguration_file")

    # Load default config
    generated_config = copy.deepcopy(DEFAULT_CONFIG)
    # Update config values from system config
    generated_config.update(load_config_from_file(system_config_path))
    # Update config values from enviroment variables
    generated_config.update(load_config_from_variables(os.environ))

    class_obj = FaddrConfig(**generated_config)
    return class_obj
