"""Get list of configuration backup files in RANCID repos."""

from itertools import chain
from pathlib import Path

from faddr import logger
from faddr.exceptions import FaddrRancidPathError

# class RancidConfig(BaseModel):
#     """Device from router.db."""
#
#
#     enabled: bool = True


class RancidGroup:
    """Rancid group dir parser.

    rancid_dir
    ├── group1                  <- This Class, self.type="group"
    │   ├── configs             <- This Class, self.type="repo"
    │   │   └── 7206-ios15-1
    │   ├── router.db
    """

    def __init__(self, path, name=None):
        self.path = Path(path)
        if not self.path.exists() or not self.path.is_dir():
            raise FaddrRancidPathError(f"Wrong path: {path}")

        if name:
            self.name = name
        else:
            self.name = self.path.name

        if Path(self.path, "router.db").exists():
            self.type = "group"
            self.repo = Path(self.path, "configs")
        else:
            self.type = "repo"
            self.repo = self.path

        if self.type == "group":
            self.configs = self.get_configs_from_router_db()
        else:
            self.configs = self.get_configs_from_dir()

        logger.debug(f"Created RancidGroup class object: {self}")

    def __repr__(self):
        return (
            f"RANCID {self.type} '{self.name}' in '{self.path}' "
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
                config["enabled"] = enabled_map.get(router_data[2], False)
                config["path"] = Path(self.repo, router_data[0])
                config["content_type"] = router_data[1]
                config["name"] = router_data[0]
                if len(router_data) == 3:
                    config["hostname"] = router_data[0]
                else:
                    config["hostname"] = router_data[3]
                config["router_db_raw_string"] = router_string
                configs.append(config)
            else:
                logger.debug(f"Ingnoring line '{router_string}' - wrong format")

        return configs

    def get_configs_from_dir(self):
        """Load config files list and their metadata from dir with files itself."""

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
                config["enabled"] = True
                config["path"] = config_path
                config["content_type"] = content_type
                config["name"] = config_path.name
                config["hostname"] = config_path.name
                configs.append(config)

        return configs

    @staticmethod
    def get_content_type(config_path):
        """Get rancid profile name from file header."""

        with Path(config_path).open(encoding="ascii", errors="ignore") as config:
            content_type_line = config.readline().strip()

        if (
            "RANCID-CONTENT-TYPE" in content_type_line
            and len(content_type_line.split(" ")) > 1
        ):
            return content_type_line.split(" ")[1]

        logger.debug(f"Couldn't detect content type in line '{content_type_line}'")
        return None


class RancidDir:
    """Rancid root dir parser.

    rancid_dir/                 <- This Class
    ├── group1
    │   ├── configs
    │   │   └── 7206-ios15-1
    │   ├── router.db
    """

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists() or not self.path.is_dir():
            raise FaddrRancidPathError(f"Wrong path: {path}")

        self.groups = []
        for group_candidate in self.path.iterdir():
            try:
                if (
                    group_candidate.is_dir()
                    and Path(group_candidate, "router.db").exists()
                ):
                    rancid_group = RancidGroup(group_candidate)
                    if len(rancid_group.configs) > 0:
                        self.groups.append(rancid_group)
            except PermissionError:
                logger.info(f"Can't access {group_candidate}")

        self.configs = chain.from_iterable(group.configs for group in self.groups)

        logger.debug(f"Created RancidGroup class object: {self}")

    def __repr__(self):
        return f"RANCID directory '{self.path}' contains {len(self.groups)} groups"

    def __str__(self):
        return str(self.path.resolve())
