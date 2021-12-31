"""Init default configuration and read configuration from file."""

# TODO: Apparently pyndatic has special class for managing settings - BaseSettings
# TODO: Use it: https://pydantic-docs.helpmanual.io/usage/settings/

import copy
import os
import pathlib
import sys

import yaml

from pydantic import BaseModel, ValidationError
from pydantic.utils import deep_update

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

EXCLUDE_VARS = ("FADDR_DEBUG", "confguration_file")


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


def load_config_from_variables(variables, prefix="", exclude_vars=EXCLUDE_VARS):
    """Parse FADDR_* enviroment variables and return FaddrConfig-compatible dict."""
    config = {}

    for var in variables:
        if var.startswith(prefix) and var not in exclude_vars:
            var_string = str(var)[len(prefix) :].casefold()
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


def load_config(
    cmd_args=None,
    default_config=DEFAULT_CONFIG,
    system_config_path=DEFAULT_SYSTEM_CONFIG_PATH,
    env_vars=os.environ,
):
    """Load config from all available sources and generate FaddrConfig object."""

    if isinstance(cmd_args, dict):
        if cmd_args.get("confguration_file") is not None:
            system_config_path = cmd_args.get("confguration_file")

    config_order = (
        "default_config",
        "system_config",
        "enviroment_config",
        "cmd_config",
    )

    config_data = {}

    # Load default config
    config_data["default_config"] = copy.deepcopy(default_config)
    logger.debug(f'Loaded default config values: {config_data["default_config"]}')

    # Get config values from system config
    config_data["system_config"] = load_config_from_file(system_config_path)
    logger.debug(f'Loaded config values from file: {config_data["system_config"]}')

    # Get config values from enviroment variables
    config_data["enviroment_config"] = load_config_from_variables(
        env_vars, prefix="FADDR_"
    )
    logger.debug(
        f'Updated config with values from enviroment variables: {config_data["enviroment_config"]}'
    )

    # Get config values from enviroment variables
    config_data["cmd_config"] = load_config_from_variables(cmd_args)
    logger.debug(
        f'Updated config with values from CMD arguments: {config_data["cmd_config"]}'
    )

    # Validate config data and create FaddrConfig object
    for config_source in config_order:
        try:
            config = FaddrConfig(
                **deep_update(config.dict(), config_data[config_source])
            )
        except NameError:
            config = FaddrConfig(**config_data[config_source])
        except ValidationError as err:
            logger.error(
                f"Config data validation for {config_source} failed: {err.errors()}"
            )
            sys.exit(1)

    logger.debug(f"Successfully validated combined config data: {config.dict()}")

    return config
