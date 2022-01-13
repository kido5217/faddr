"""Get list of configuration backup files in RANCID repos."""

import pathlib

from faddr import logger
from faddr.exceptions import (
    FaddrRancidRepoUnsupportedLevel,
    FaddrRancidRepoPathError,
    FaddrRancidRepoConfigFileFormatError,
    FaddrRancidRepoRouterDBAbsent,
)


class RancidDir:
    """Analyze dir and find rancid repos/backup files.

    path can be one of three levels of Rancid base dir:

    rancid_dir/                 <- "root"
    ├── group1                  <- "group"
    │   ├── configs             <- "repo"
    │   │   └── 7206-ios15-1
    │   ├── router.db

    """

    def __init__(self, path, level) -> None:
        if level in ("root", "group", "repo"):
            self.level = level
        else:
            raise FaddrRancidRepoUnsupportedLevel

        path = pathlib.Path(path)
        if path.exists() and path.is_dir():
            self.path = path
        else:
            raise FaddrRancidRepoPathError(path)

        self.configs = []

        if self.level in ("repo", "group"):
            self.groups = [self.path.name]
            self.configs.extend(self.get_configs(self.path))

        elif self.level == "root":
            pass

    def get_configs(self, path):
        """Make list of dicts with config file data."""
        configs = []
        if self.level == "repo":
            path = pathlib.Path(path)
            # With repo level, group name equals to dir name and all devices are enabled
            group = path.name
            for child in path.iterdir():
                if child.is_file():
                    try:
                        config = {}
                        config["content_type"] = self.get_content_type(child)
                        config["group"] = group
                        config["path"] = child
                        config["enabled"] = True
                        configs.append(config)
                    except FaddrRancidRepoConfigFileFormatError:
                        logger.info(f"File {child} isn't valid rancid config backup")
        else:
            group = pathlib.Path(path).name
            router_db_path = pathlib.Path(path, "router.db")
            if router_db_path.exists():
                configs = self.parse_router_db(router_db_path)

            else:
                raise FaddrRancidRepoRouterDBAbsent

        return configs

    @staticmethod
    def get_content_type(path, encoding="ascii", errors="ignore"):
        """Get rancid content type from file."""
        with pathlib.Path(path).open(encoding=encoding, errors=errors) as config_file:
            content_type_string = config_file.readline().strip().split(" ")
        if len(content_type_string) == 2:
            content_type = content_type_string[1]
        else:
            raise FaddrRancidRepoConfigFileFormatError(path)
        return content_type

    @staticmethod
    def parse_router_db(path, encoding="ascii", errors="ignore"):
        """Parse router.db file into list of dicts."""
        configs = []
        is_enabled_map = {
            "up": True,
            "down": False,
        }
        router_db_path = pathlib.Path(path)
        group = router_db_path.parent.name

        with router_db_path.open(encoding=encoding, errors=errors) as router_db:
            for device_string in router_db.readlines():
                # Ignore conneted out devices
                if device_string.startswith("#"):
                    logger.info(f"Ingoring device {device_string} in {router_db_path}")
                    continue

                if ";" in device_string:
                    sep = ";"
                else:
                    sep = ":"

                device = device_string.split(sep)
                if len(device) == 3:
                    config = {}
                    config["path"] = router_db_path.parent.joinpath(
                        "configs", device[0]
                    )
                    config["content_type"] = device[1]
                    config["group"] = group
                    config["enabled"] = is_enabled_map.get(device[2], False)
                    configs.append(config)
                elif len(device) == 4:
                    config = {}
                    config["path"] = router_db_path.parent.joinpath(
                        "configs", device[0]
                    )
                    config["content_type"] = device[2]
                    config["group"] = group
                    config["enabled"] = is_enabled_map.get(device[3], False)
                    configs.append(config)
                else:
                    logger.info(
                        f"Malformed device string {device} in {router_db_path}, ignoring"
                    )

        return configs
