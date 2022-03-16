"""Configuration file parser."""

from pathlib import Path

from ttp import ttp

from faddr import logger
from faddr.exceptions import (
    FaddrParserConfigFileAbsent,
    FaddrParserConfigFileEmpty,
    FaddrParserUnknownProfile,
)


class Parser:
    """Loads configuration, preprocesses it, parses it and returns structured data."""

    SUPPORTED_PROFILES = (
        "cisco-ios",
        "cisco-iosxr",
        "huawei-vrp",
        "juniper-junos",
    )

    def __init__(
        self,
        config,
        profile,
        template_dir,
    ) -> None:

        if profile in self.__class__.SUPPORTED_PROFILES:
            self.profile = profile
            logger.debug(f"Using profile '{self.profile}'")
        else:
            raise FaddrParserUnknownProfile(profile)

        self.template = self.load_template(template_dir)

        self.raw_config = self.load_config(config)
        self.config = self.cleanup_config(self.raw_config)

    def __str__(self) -> str:
        return self.profile

    def load_template(self, template_dir):
        """Load ttp template from template dir."""
        template_name = self.profile + ".ttp"
        template_path = Path(template_dir, template_name)
        with open(template_path, encoding="ascii", errors="ignore") as template_file:
            return template_file.read()

    def load_config(self, config):
        """Config loader."""

        if isinstance(config, Path):
            logger.debug(f"Provided config is path to file: '{config}'")
            return self.load_config_from_file(config)

        if isinstance(config, list):
            if len(config) == 1:
                logger.debug(f"Provided config is path to file: '{config[0]}'")
                return self.load_config_from_file(config[0])
            return "\n".join(config)

        if isinstance(config, str):
            if len(config.split("\n")) == 1:
                logger.debug(f"Provided config is path to file: '{config}'")
                return self.load_config_from_file(config)

        return config

    def load_config_from_file(self, path):
        """Try to read data from file."""
        path = Path(path)
        if not path.exists():
            raise FaddrParserConfigFileAbsent(path)

        with open(path, encoding="ascii", errors="ignore") as config_file:
            config = config_file.read()

        if len(config) == 0:
            raise FaddrParserConfigFileEmpty(path)

        return config

    def cleanup_config(self, config):
        """Vendor/profile specific config preprocessing."""
        clean_config = config
        return clean_config

    def parse(self):
        """Parse provided configuration and return structured data."""
        parser = ttp(data=self.config, template=self.template)
        parser.parse()
        result = parser.result()[0][0]
        return result
