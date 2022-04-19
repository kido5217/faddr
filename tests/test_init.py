"""PyTest tests for faddr package."""

from faddr import __version__


def test_version():
    """Test app version."""
    assert __version__ == "0.3.1"
