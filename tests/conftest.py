"""PyTest fixtures that are accessible by all tests."""

import pathlib

import pytest


@pytest.fixture
def config_file_absent():
    """Absent config file."""
    return pathlib.Path("tests/fixtures/nonexistant_config.yaml")


@pytest.fixture
def config_empty():
    """Empty config."""
    return {}


@pytest.fixture
def config_file_valid():
    """Valig config file."""
    return pathlib.Path("tests/fixtures/faddr_config_valid.yaml")


@pytest.fixture
def config_valid():
    """Valid config dictionary."""
    config = {
        "database": {
            "dir": "data/",
            "file": "faddr-db.json",
        },
        "rancid": {
            "dir": "tests/fixtures/rancid_dir/",
            "mapping": {
                "cisco-mf": "cisco_ios",
            },
        },
    }
    return config


@pytest.fixture
def config_file_invalid():
    """Broken yaml file."""
    return pathlib.Path("tests/fixtures/faddr_config_invalid.yaml")
