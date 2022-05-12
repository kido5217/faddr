"""Config repository's rapser."""

from itertools import chain
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from faddr.exceptions import FaddrRepoPathError, FaddrRepoUnsupported
from faddr.logging import logger
from faddr.rancid import RancidDir


class Config(BaseModel):
    """Config dataclass."""

    path: Path
    name: str
    profile: str
    source: str


class Repo:
    """Repo class for config repository"""

    SUPPORTED_REPOS = ("rancid",)

    def __init__(self, path, kind, mapping=None):
        if mapping is None:
            self.mapping = {}
        else:
            self.mapping = mapping

        if kind not in self.SUPPORTED_REPOS:
            raise FaddrRepoUnsupported(kind)
        self.kind = kind

        self.path = Path(path)
        if not self.path.exists():
            raise FaddrRepoPathError(path)

        if self.kind == "rancid":
            self.data = RancidDir(path)

    @property
    def configs(self):
        """Unified config list."""
        configs = []
        for config_raw_data in self.data.configs:
            config_data = {
                "path": config_raw_data.get("path"),
                "name": config_raw_data.get("name"),
                "profile": self.mapping.get(
                    config_raw_data.get("content_type"),
                    config_raw_data.get("content_type"),
                ),
                "source": self.kind,
            }
            try:
                config = Config.parse_obj(config_data)
            except ValidationError as err:
                logger.warning(f"Failed to parse config {config_data}: {str(err)}")
            else:
                configs.append(config)
        return configs


class RepoList:
    """Aggregated list of repo objects."""

    def __init__(self, mapping=None):
        if mapping is None:
            self.mapping = {}
        else:
            self.mapping = mapping
        self.repos = []

    def parse_file(self, path):
        """Load repo list and mapping from file."""
        path = Path(path)
        if not path.exists():
            raise FaddrRepoPathError(path)

        with open(path, encoding="ascii", errors="ignore") as repo_file:
            repos_data = yaml.safe_load(repo_file)
            mapping = repos_data.get("mapping", self.mapping)
            repos = repos_data.get("repos", [])
            logger.info(f"Repo file {path} contains {len(repos)} repos.")
            if len(repos) == 0:
                logger.warning(f"Repo file {path} contains no repos.")

            for repo_data in repos:
                try:
                    repo = Repo(
                        repo_data.get("path"),
                        repo_data.get("kind", "rancid"),
                        repo_data.get("mapping", mapping),
                    )
                except ValidationError as err:
                    logger.warning(f"Failed to add {repo_data} to RepoList: {str(err)}")
                else:
                    self.repos.append(repo)

    @property
    def configs(self):
        """Aggregate configs form all repos."""
        configs = chain.from_iterable(repo.configs for repo in self.repos)
        return configs
