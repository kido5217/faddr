"""Init default configuration and read configuration from file."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from pydantic import BaseModel, BaseSettings, ValidationError
from pydantic.env_settings import SettingsSourceCallable

from faddr import logger
from faddr.exceptions import FaddrSettingsFileFormatError


def load_settings(settings_file=None):
    """Settings loader."""

    if settings_file:
        FaddrSettings.Config.settings_file = settings_file

    try:
        settings = FaddrSettings()
    except ValidationError as err:
        logger.debug(f"Failed to parse configuration file '{settings_file}': {err}")
        raise FaddrSettingsFileFormatError(settings_file, err) from None
    return settings


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


class RancidDirSettings(BaseModel):
    """Rancid Directory settings."""

    path: str = "/var/lib/rancid/"
    mapping: dict = {}


class RancidSettings(BaseModel):
    """Rancid settings."""

    dirs: List[RancidDirSettings] = [RancidDirSettings()]
    mapping: dict = {
        "cisco": "cisco-ios",
        "cisco-xr": "cisco-iosxr",
        "juniper": "juniper-junos",
    }


class FaddrSettings(BaseSettings):
    """Faddr settings root."""

    debug: bool = False
    templates_dir: Path = Path(__file__).parent.joinpath("templates")
    database: DatabaseSettings = DatabaseSettings()
    rancid: RancidSettings = RancidSettings()

    class Config:
        """pydantic configuration."""

        env_prefix = "faddr_"
        settings_file = "/etc/faddr/faddr.yaml"

        @classmethod
        # pylint: disable=unused-argument
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Only return init settings and settings loaded from settings file."""
            return (init_settings, yaml_config_settings_source, env_settings)
