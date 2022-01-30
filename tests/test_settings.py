"""PyTest tests for configuration dataclasses, functions and defaults."""

import pathlib

import pytest

from pydantic import ValidationError

from faddr.settings import (
    FaddrConfig,
    DEFAULT_CONFIG,
    DEFAULT_SYSTEM_CONFIG_PATH,
    load_config_from_file,
)


def test_validate_default_config():
    """Test if default configuration works with configuration dataclasses."""
    try:
        FaddrConfig(**DEFAULT_CONFIG)
    except ValidationError as err:
        pytest.fail(err)


def test_validate_default_system_config_path():
    """Test if default system config path can be parsed with pathlib."""
    try:
        pathlib.Path(DEFAULT_SYSTEM_CONFIG_PATH)
    except Exception as err:
        pytest.fail(err)


@pytest.mark.parametrize(
    "config_file_path,config",
    [
        ("config_file_absent", "config_empty"),
        ("config_file_valid", "config_valid"),
        ("config_file_invalid", "config_empty"),
    ],
)
def test_load_config_from_file(config_file_path, config, request):
    """Test reading config grom file."""
    config_file_path = request.getfixturevalue(config_file_path)
    config = request.getfixturevalue(config)
    loaded_config = load_config_from_file(config_file_path)
    assert loaded_config == config
