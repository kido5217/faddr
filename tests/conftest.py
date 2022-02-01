"""PyTest fixtures that are accessible by all tests."""

import pathlib

import pytest


@pytest.fixture
def settings_default():
    """Default settings."""
    settings = {
        "debug": False,
        "templates_dir": pathlib.Path(__file__)
        .parent.with_name("faddr")
        .joinpath("templates"),
        "database": {"dir": "/var/db/faddr/", "file": "faddr-db.json"},
        "rancid": {
            "dirs": [{"path": "/var/lib/rancid/", "kind": "dir", "mapping": {}}],
            "default_mapping": {
                "cisco": "cisco_ios",
                "cisco-xr": "cisco_iosxr",
                "juniper": "juniper_junos",
            },
            "mapping": {},
        },
    }
    return settings


@pytest.fixture
def settings_posix_tmp():
    """Settings with output dir as '/tmp'"""
    settings = {
        "debug": False,
        "templates_dir": pathlib.Path(__file__)
        .parent.with_name("faddr")
        .joinpath("templates"),
        "database": {"dir": "/tmp/", "file": "faddr-db.json"},
        "rancid": {
            "dirs": [
                {
                    "path": "tests/fixtures/rancid/",
                    "kind": "dir",
                    "mapping": {"cisco-faddr": "cisco_ios"},
                }
            ],
            "default_mapping": {
                "cisco": "cisco_ios",
                "cisco-xr": "cisco_iosxr",
                "juniper": "juniper_junos",
            },
            "mapping": {},
        },
    }
    return settings


@pytest.fixture
def settings_file_absent():
    """Absent settings file."""
    return pathlib.Path("tests/fixtures/nonexistant_settings_file.yaml")


@pytest.fixture
def settings_file_posix_tmp():
    """Settings file with output dir as '/tmp'."""
    return pathlib.Path("tests/fixtures/faddr_posix_tmp.yaml")


@pytest.fixture
def settings_file_malformed():
    """Corrupted settings file.'"""
    return pathlib.Path("tests/fixtures/faddr_malformed.yaml")


@pytest.fixture
def settings_file_wrong_format():
    """Wrong format settings file.'"""
    return pathlib.Path("tests/fixtures/faddr_wrong_format.yml")
