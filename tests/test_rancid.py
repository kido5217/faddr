"""RancidDir and RancidGroup classes unit tests."""

import pytest

from faddr.exceptions import FaddrRancidPathError
from faddr.rancid import RancidDir, RancidGroup


def test_rancid_dir_class_creation():
    """Check if RancidDir class instance can be created."""
    rancid_dir = RancidDir("tests/fixtures/rancid")
    assert isinstance(rancid_dir, RancidDir)


def test_rancid_dir_path_verification():
    """Exception should be raised if input dir doesn't exist."""
    with pytest.raises(FaddrRancidPathError):
        RancidDir("tests/fixtures/nonexistent_dir")


def test_rancid_group_class_creation():
    """Check if RancidGroup class instance can be created."""
    rancid_dir = RancidGroup("tests/fixtures/rancid/group_01_3rows")
    assert isinstance(rancid_dir, RancidGroup)


def test_rancid_group_repo_class_creation():
    """Check if RancidGroup class instance can be created, repo type."""
    rancid_dir = RancidGroup("tests/fixtures/rancid/group_01_3rows/configs")
    assert isinstance(rancid_dir, RancidGroup)


def test_rancid_group_repo_name():
    """Check if RancidGroup class instance can be created with specified name."""
    test_name = "TestName"
    rancid_dir = RancidGroup(
        "tests/fixtures/rancid/group_01_3rows/configs", name=test_name
    )
    assert rancid_dir.name == test_name
