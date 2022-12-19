"""Get list of configuration backup files in RANCID repos."""

import time
from itertools import chain
from pathlib import Path

from faddr.exceptions import FaddrRancidPathError
from faddr.logging import logger


def expire_configs(config_candidates, file_age_limit):
    """Remove from list files that are older than provided limit."""
    configs = []
    for config in config_candidates:
        file_mtime = config["path"].stat().st_mtime
        logger.debug(f'Config file {config["path"]} was modified at {file_mtime}')
        if time.time() - file_mtime < file_age_limit:
            configs.append(config)
        else:
            logger.debug(f'Config file {config["path"]} is too old, skipping')
    return configs


class RancidGroup:
    """Rancid group dir parser."""

    def __init__(self, path, name=None, file_age_limit=604800):
        self.path = Path(path)
        if not self.path.exists() or not self.path.is_dir():
            raise FaddrRancidPathError(path)

        if name:
            self.name = name
        else:
            self.name = self.path.name

        self.file_age_limit = file_age_limit

        if Path(self.path, "router.db").exists():
            self.level = "group"
            self.repo = Path(self.path, "configs")
            self.configs = self.get_configs_from_router_db()
        else:
            self.level = "repo"
            self.repo = self.path
            self.configs = self.get_configs_from_dir()

        logger.debug(f"Created RancidGroup class object: {self}")

    def __repr__(self):
        return (
            f"RANCID {self.level} '{self.name}' in '{self.path}' "
            f"contains {len(self.configs)} configs"
        )

    def __str__(self):
        return self.name

    def get_configs_from_router_db(self):
        """Load config files list and their metadata from 'router.db' file."""

        configs = []

        with Path(self.path, "router.db").open(
            encoding="ascii", errors="ignore"
        ) as router_db_file:
            router_db = router_db_file.readlines()

        for router_string in router_db:
            if router_string.startswith("#"):
                logger.debug(f"Ignoring line '{router_string}' - commented out")
                continue

            if ";" in router_string:
                sep = ";"
            else:
                sep = ":"

            # router.db is actually a csv file, but python's csv's builtin
            # dialect parser didn't work for me, so manual parsing for now
            router_data = router_string.strip().strip(";:").split(sep)
            if len(router_data) == 3 or len(router_data) == 4:
                config = {}
                enabled_map = {"up": True, "down": False}
                config["is_enabled"] = enabled_map.get(router_data[2], False)
                config["path"] = Path(self.repo, router_data[0].casefold())
                config["content_type"] = router_data[1]
                config["name"] = router_data[0].casefold()
                if len(router_data) == 3:
                    config["hostname"] = router_data[0].casefold()
                else:
                    config["hostname"] = router_data[3].casefold()
                configs.append(config)
            else:
                logger.debug(f"Ingnoring line '{router_string}' - wrong format")

        configs = expire_configs(configs, self.file_age_limit)

        return configs

    def get_configs_from_dir(self):
        """Load config files list and their metadata from dir with files themselves."""

        configs = []

        for config_path in self.repo.iterdir():
            if not config_path.is_file():
                logger.debug(f"Skipping '{config_path}' - not a file")
                continue

            if config_path.stat().st_size == 0:
                logger.debug(f"Skipping '{config_path}' - file is empty")
                continue

            content_type = self.get_content_type(config_path)
            if content_type:
                config = {}
                config["is_enabled"] = True
                config["path"] = config_path
                config["content_type"] = content_type
                config["name"] = config_path.name
                config["hostname"] = config_path.name
                configs.append(config)

        configs = expire_configs(configs, self.file_age_limit)

        return configs

    @staticmethod
    def get_content_type(config_path):
        """Get rancid profile name from file header."""

        with Path(config_path).open(encoding="ascii", errors="ignore") as config:
            content_type_line = config.readline().strip()

        if len(content_type_line.split("RANCID-CONTENT-TYPE:")) > 1:
            return content_type_line.split("RANCID-CONTENT-TYPE:")[-1].strip()

        logger.debug(f"Couldn't detect content type in line '{content_type_line}'")
        return None


class RancidDir:
    """Rancid root dir parser."""

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists() or not self.path.is_dir():
            raise FaddrRancidPathError(f"Wrong path: {path}")

        self.level = self.get_level(path)

        self.groups = []

        if self.level == "dir":
            for group_candidate in self.path.iterdir():
                try:
                    group = RancidGroup(group_candidate)
                    self.groups.append(group)
                except (FaddrRancidPathError, PermissionError):
                    logger.warning(f"{group_candidate} isn't valid rancid group dir")

            if len(self.groups) == 0:
                raise FaddrRancidPathError(self.path)
        else:
            self.groups.append(RancidGroup(self.path))

        self.configs = chain.from_iterable(group.configs for group in self.groups)

        logger.debug(f"Created RancidGroup class object: {self}")

    def __repr__(self):
        return f"RANCID directory '{self.path}' contains {len(self.groups)} groups"

    def __str__(self):
        return str(self.path.resolve())

    @staticmethod
    def get_level(path):
        """Get level inside rancid dir for provided path."""
        path = Path(path)

        if Path(path, "router.db").exists():
            return "group"

        for group_candidate in path.iterdir():
            try:
                if Path(group_candidate, "router.db").exists():
                    return "dir"
            except PermissionError:
                logger.warning(f"Can't access {group_candidate}")

        for config_path in path.iterdir():
            try:
                if config_path.is_file():
                    with config_path.open(encoding="ascii", errors="ignore") as config:
                        ct_line = config.readline()
                    if "RANCID-CONTENT-TYPE" in ct_line:
                        return "repo"
            except PermissionError:
                logger.warning(f"Can't access {config_path}")

        raise FaddrRancidPathError(path)
