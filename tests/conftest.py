"""PyTest fixtures that are accessible by all tests"""

import dataclasses
import pathlib

import pytest

from faddr.dataclasses import Interface, IPv4, Vlan


@pytest.fixture
def cisco_ios_simple_config_path():
    """Returns Path-object for default test config"""
    cisco_ios_simple_config_path = pathlib.Path(
        "tests/fixtures/config_snippets/cisco_ios/simple_config.conf"
    )
    return cisco_ios_simple_config_path


@pytest.fixture
def cisco_ios_simple_config_raw(cisco_ios_simple_config_path):
    """Reads config from file to list of strings"""
    with open(cisco_ios_simple_config_path, mode="r", errors="ignore") as config_file:
        raw_config = config_file.readlines()
    return raw_config


@pytest.fixture
def cisco_ios_simple_config(cisco_ios_simple_config_path):
    """Creares raw cisco config of comments etc"""
    with open(cisco_ios_simple_config_path, mode="r", errors="ignore") as config_file:
        raw_config = config_file.readlines()
    config = []
    for line in raw_config:
        line = line.rstrip()
        if line.startswith("!") is False:
            config.append(line)
    return config


@pytest.fixture
def cisco_ios_l3_simple_raw():
    raw_config = [
        "interface FastEthernet0/0.100",
        ' description "Test logical subinterface"',
        " encapsulation dot1Q 100",
        " ip address 10.1.1.1 255.255.255.252",
    ]
    return raw_config


@pytest.fixture
def cisco_ios_l3_simple_parsed():
    vlan = Vlan("100", encapsulation="dot1Q")
    ipv4 = IPv4("10.1.1.1", mask="255.255.255.252")
    interface = Interface(
        "FastEthernet0/0.100",
        description='"Test logical subinterface"',
        vlans=[vlan],
        ipv4=[ipv4],
    )
    parsed_config = dataclasses.asdict(interface)
    return parsed_config


@pytest.fixture
def cisco_ios_l3_vrf():
    return None


@pytest.fixture
def cisco_ios_l3_acl():
    return None


@pytest.fixture
def cisco_ios_l3_multiple_ipv4():
    return None


@pytest.fixture
def cisco_ios_l3_shutdown():
    return None
