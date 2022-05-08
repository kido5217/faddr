"""Init default configuration and read configuration from file."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from pydantic import BaseModel, BaseSettings

from faddr import logger
from faddr.exceptions import FaddrSettingsFileFormatError


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """A simple settings source that loads variables from a YAML file."""

    settings_file_path = Path(settings.__config__.settings_file)
    if settings_file_path.exists():
        try:
            with open(
                settings_file_path,
                encoding="ascii",
                errors="ignore",
            ) as settings_file:
                return yaml.safe_load(settings_file)
        except yaml.scanner.ScannerError as err:
            logger.debug(
                f"Failed to parse configuration file '{settings_file_path}': {err}"
            )
            raise FaddrSettingsFileFormatError(settings_file_path, err) from None
    return {}


class DatabaseSettings(BaseModel):
    """Database settings."""

    path: str = "/var/db/faddr/"
    name: str = "faddr-db.sqlite"
    revisions: int = 10


class FaddrSettings(BaseSettings):
    """Faddr settings root."""

    debug: bool = False
    processes: int = 1
    templates_dir: Path = Path(__file__).parent.joinpath("templates")
    database: DatabaseSettings = DatabaseSettings()
    repo_file = "/etc/faddr/faddr.yaml"
    mapping: dict = {
        "cisco": "cisco-ios",
        "cisco-xr": "cisco-iosxr",
        "juniper": "juniper-junos",
        "huawei": "huawei-vrp",
    }

    class Config:
        """pydantic settings parser configuration."""

        env_prefix = "faddr_"
        env_nested_delimiter = "__"
        env_file = ".env"
