"""Init default configuration and read configuration from file."""

import pathlib
from typing import Any, Dict, List, Tuple

import yaml
from pydantic import BaseModel, BaseSettings
from pydantic.env_settings import SettingsSourceCallable


def load_settings(settings_file):
    """Settings loader."""

    if settings_file:
        FaddrSettings.Config.settings_file = settings_file

    settings = FaddrSettings()
    return settings


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """A simple settings source that loads variables from a YAML file."""

    settings_file_path = pathlib.Path(settings.__config__.settings_file)
    if settings_file_path.exists():
        with open(
            settings_file_path,
            encoding="ascii",
            errors="ignore",
        ) as settings_file:
            return yaml.safe_load(settings_file)

    return {}


class DatabaseSettings(BaseModel):
    """Database settings."""

    dir: str = "/var/db/faddr/"
    file: str = "faddr-db.json"


class RancidDirSettings(BaseModel):
    """Rancid Directory settings."""

    path: str = "/var/lib/rancid/"
    kind: str = "dir"
    mapping: dict = {}


class RancidSettings(BaseModel):
    """Rancid settings."""

    dirs: List[RancidDirSettings] = [RancidDirSettings()]
    default_mapping: dict = {
        "cisco": "cisco_ios",
        "cisco-xr": "cisco_iosxr",
        "juniper": "juniper_junos",
    }
    mapping: dict = {}


class FaddrSettings(BaseSettings):
    """Faddr settings root."""

    database: DatabaseSettings = {}
    rancid: RancidSettings = {}

    class Config:
        """pydantic configuration."""

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
            return (init_settings, yaml_config_settings_source)
