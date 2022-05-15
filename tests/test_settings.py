"""PyTest tests for configuration dataclasses, functions and defaults."""

from faddr.settings import FaddrSettings


def test_load_settings_default(settings_default):
    """Test loading settings with no settings file."""
    settings = FaddrSettings(_env_file=None)
    assert settings.dict() == settings_default
