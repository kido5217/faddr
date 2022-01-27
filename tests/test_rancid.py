"""RancidDir and RancidGroup classes unit tests."""

from faddr import RancidDir, RancidGroup


def test_rancid_dir_class_creation():
    """Check if class instance can be created."""
    rancid_dir = RancidDir("tests/fixtures/rancid")
    assert isinstance(rancid_dir, RancidDir)
