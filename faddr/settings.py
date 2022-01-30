"""Init default configuration and read configuration from file."""

from typing import List

from pydantic import BaseModel, BaseSettings


class DatabaseSettings(BaseModel):
    """Database settings."""

    dir: str = "/var/db/faddr/"
    file: str = "faddr.json"


class RancidDirSettings(BaseModel):
    """Rancid Directory settings."""

    kind: str = "dir"
    path: str = "/var/lib/rancid/"
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


class Settings(BaseSettings):
    """Faddr settings root."""

    database: DatabaseSettings = {}
    rancid: RancidSettings = {}
