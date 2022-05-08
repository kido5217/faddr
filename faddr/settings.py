"""Init default configuration and read configuration from file."""

from pathlib import Path

from pydantic import BaseModel, BaseSettings


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
