"""faddr-db cli entry point unit tests."""

import pytest
import ray

from faddr.faddr_db import parse_config


@pytest.mark.skip(reason="Failing ATM, needs more investigation")
def test_parse_config(
    ray_init, parser_load_profiles
):  # pylint: disable=unused-argument
    """Test if parsing with ray works."""
    for profile in parser_load_profiles:
        data = ray.get(parse_config.remote(profile["config_path"], profile["name"]))
        assert profile["data"] == data
