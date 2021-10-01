import pathlib
from typing import List

import pytest

from faddr import Device, CiscoIOSDevice, device
from faddr.exceptions import FaddrDeviceUnsupportedType


@pytest.fixture
def cisco_ios_simple_config_path():
    cisco_ios_simple_config_path = pathlib.Path(
        "tests/fixtures/config_snippets/cisco_ios/simple_config.conf"
    )
    return cisco_ios_simple_config_path


@pytest.fixture
def cisco_ios_simple_config_raw(cisco_ios_simple_config_path):
    with open(cisco_ios_simple_config_path, mode="r", errors="ignore") as config_file:
        raw_config = config_file.readlines()
    return raw_config


@pytest.fixture
def cisco_ios_simple_config(cisco_ios_simple_config_path):
    with open(cisco_ios_simple_config_path, mode="r", errors="ignore") as config_file:
        raw_config = config_file.readlines()
    config = []
    for line in raw_config:
        line = line.rstrip()
        if line.startswith("!") is False:
            config.append(line)
    return config


@pytest.mark.parametrize(
    "device_type,device_class",
    [("cisco", CiscoIOSDevice), ("cisco_ios", CiscoIOSDevice)],
)
def test_device_factory(device_type, device_class):
    assert isinstance(Device(None, device_type=device_type), device_class)


def test_device_factory_exception():
    with pytest.raises(FaddrDeviceUnsupportedType):
        Device(None, device_type="some_random_device")


def test_cisco_ios_create_object(cisco_ios_simple_config_path):
    device = CiscoIOSDevice(cisco_ios_simple_config_path)
    assert device.device_type == "cisco_ios"
    assert device.config_path == cisco_ios_simple_config_path
    assert device.data == None


def test_cisco_ios_read_config(
    cisco_ios_simple_config_path, cisco_ios_simple_config_raw, cisco_ios_simple_config
):
    device = CiscoIOSDevice(cisco_ios_simple_config_path)
    device.read_config()
    assert device.raw_config == cisco_ios_simple_config_raw
    assert device.config == cisco_ios_simple_config
