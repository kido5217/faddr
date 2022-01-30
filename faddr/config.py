"""Settings loader, powered by dynaconf module."""

import sys
from dynaconf import Dynaconf

from faddr import logger


def load_settings(cli_args=None):
    """Create dynacond settings object from input data."""
    if not cli_args:
        cli_args = {}
        logger.debug("No arguments received from cli, useng default settings")

    settings_file = cli_args.get("settings_file", "/etc/faddr/faddr.yaml")

    print(sys.path)
    settings = Dynaconf(
        settings_files=["faddr/default_settings.yaml", settings_file],
        environments=False,
        load_dotenv=False,
    )
    return settings
