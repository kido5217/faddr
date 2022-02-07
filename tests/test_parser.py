"""Parser class unit tests."""

from pathlib import Path

import pytest

from faddr.exceptions import FaddrParserUnknownProfile
from faddr.parser import Parser


def test_parser_unknown_profile():
    """Test if exception is raised with unknown profile."""
    with pytest.raises(FaddrParserUnknownProfile):
        Parser("\n\n", "UNSUPPORTED_PROFILE", "")


def test_parser_to_str(parser_load_profiles, template_dir_embedded):
    """Test Parser class __str__ method."""
    for profile in parser_load_profiles:
        assert profile["name"] == str(
            Parser(profile["config_path"], profile["name"], template_dir_embedded)
        )


def test_parser_parse_declared_profiles_config_path(
    parser_load_profiles, template_dir_embedded
):
    """Test if all profiles can successfully parse simple config provided as path."""
    for profile in parser_load_profiles:
        parser = Parser(profile["config_path"], profile["name"], template_dir_embedded)
        assert profile["data"] == parser.parse()


def test_parser_parse_declared_profiles_config_str(
    parser_load_profiles, template_dir_embedded
):
    """Test if all profiles can successfully parse simple config provided as string."""
    for profile in parser_load_profiles:
        parser = Parser(profile["config"], profile["name"], template_dir_embedded)
        assert profile["data"] == parser.parse()


def test_parser_parse_declared_profiles_config_list(
    parser_load_profiles, template_dir_embedded
):
    """Test if all profiles can successfully parse simple config provided as list."""
    for profile in parser_load_profiles:
        parser = Parser(profile["config_list"], profile["name"], template_dir_embedded)
        assert profile["data"] == parser.parse()
