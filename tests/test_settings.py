"""PyTest tests for configuration dataclasses, functions and defaults."""

import pathlib

import pytest

from faddr.settings import load_settings


def test_load_settings_default(settings_default):
    """Test loading settings with no settings file."""
    settings = load_settings()
    assert settings == settings_default


def test_load_settings_file_absent(settings_default, settings_file_absent):
    """Test loading settings with absent settings file."""
    settings = load_settings(settings_file_absent)
    assert settings == settings_default


def test_load_settings_posix_tmp(settings_posix_tmp, settings_file_posix_tmp):
    """Test loading settings with working settings file."""
    settings = load_settings(settings_file_posix_tmp)
    assert settings == settings_posix_tmp
