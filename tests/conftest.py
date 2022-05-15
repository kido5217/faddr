"""PyTest fixtures that are accessible by all tests."""

import json
from pathlib import Path

import pytest
import ray

from faddr.parser import Parser


@pytest.fixture
def settings_default():
    """Default settings."""
    settings = {
        "debug": False,
        "log_level": "INFO",
        "processes": 1,
        "templates_dir": Path(__file__).parent.with_name("faddr").joinpath("templates"),
        "mapping": {
            "cisco": "cisco-ios",
            "cisco-xr": "cisco-iosxr",
            "juniper": "juniper-junos",
            "huawei": "huawei-vrp",
        },
        "database": {
            "path": "/var/db/faddr/",
            "name": "faddr-db.sqlite",
            "revisions": 10,
        },
        "api": {"host": "0.0.0.0", "port": 8000, "workers": 1},
        "repo_file": "/etc/faddr/faddr.yaml",
    }
    return settings


def parser_get_config_path(profile):
    """Get config name for provided profile."""
    config_name = profile + ".conf"
    config = Path("tests/fixtures/ttp", config_name)
    return config


def parser_get_config(profile):
    """Get config for provided profile."""
    path = parser_get_config_path(profile)
    with open(path, mode="r", encoding="ascii") as config_file:
        config = config_file.read()
    return config


def parser_get_config_list(profile):
    """Get config as list for provided profile."""
    path = parser_get_config_path(profile)
    with open(path, mode="r", encoding="ascii") as config_file:
        config = config_file.readlines()
    return config


def parser_get_data(profile):
    """Get config data for provided profile."""
    data_name = profile + ".json"
    data_path = Path("tests/fixtures/ttp", data_name)
    with open(data_path, mode="r", encoding="ascii") as data_file:
        data = json.load(data_file)
    return data


@pytest.fixture
def parser_load_profiles():
    """Get simple config and it's parsed data."""
    profiles = []
    for profile_name in Parser.SUPPORTED_PROFILES:
        profile = {"name": profile_name}

        profile["config_path"] = parser_get_config_path(profile_name)
        profile["config"] = parser_get_config(profile_name)
        profile["config_list"] = parser_get_config_list(profile_name)
        profile["data"] = parser_get_data(profile_name)

        profiles.append(profile)
    return profiles


@pytest.fixture
def template_dir_embedded():
    """Get faddr's embedded template dir."""
    templates_dir = Path(__file__).parent.with_name("faddr").joinpath("templates")
    return templates_dir


@pytest.fixture(scope="module")
def ray_init():
    """Init ray only ones per tests run and with one process."""
    ray.init(local_mode=True)
    yield None
    ray.shutdown()
