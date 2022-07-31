"""Init default configuration and read configuration from file."""

from pathlib import Path

from pydantic import BaseModel, BaseSettings, validator


class DatabaseSettings(BaseModel):
    """Database settings."""

    path: str = "/var/db/faddr/"
    name: str = "faddr-db.sqlite"
    revision_limit: int = 10


class APISettings(BaseModel):
    """REST API settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


class FaddrSettings(BaseSettings):
    """Faddr settings root."""

    debug: bool = False
    log_level: str = "INFO"
    processes: int = 1
    templates_dir: Path = Path(__file__).parent.joinpath("templates")
    repo_file = "/etc/faddr/faddr.yaml"
    mapping: dict = {
        "cisco": "cisco-ios",
        "cisco-xr": "cisco-iosxr",
        "juniper": "juniper-junos",
        "huawei": "huawei-vrp",
    }

    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()

    class Config:  # pylint: disable=too-few-public-methods
        """pydantic settings parser configuration."""

        env_prefix = "faddr_"
        env_nested_delimiter = "__"
        env_file = ".env"

    @validator("log_level")
    def set_log_level_from_debug_key(
        cls, value, values
    ):  # pylint: disable=no-self-argument,no-self-use
        """If debug is enabled, set the log level to debug too."""
        if values.get("debug", False):
            value = "DEBUG"
        return value
