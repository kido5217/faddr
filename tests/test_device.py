"""PyTest tests for Device Classes"""

import pytest

from ciscoconfparse import CiscoConfParse

from faddr import Device, CiscoIOSDevice
from faddr.exceptions import FaddrDeviceUnsupportedType


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
    assert device.data is None


def test_cisco_ios_read_config(
    cisco_ios_simple_config_path, cisco_ios_simple_config_raw, cisco_ios_simple_config
):
    device = CiscoIOSDevice(cisco_ios_simple_config_path)
    device.read_config()
    assert device.raw_config == cisco_ios_simple_config_raw
    assert device.config == cisco_ios_simple_config


@pytest.mark.skip(reason="WIP")
def test_cisco_ios_create_parser():
    device = CiscoIOSDevice(None)
    device.config = []
    parser = device.__get_parser()
    assert isinstance(parser, CiscoConfParse)


@pytest.mark.parametrize(
    "raw_config,parsed_config",
    [
        ("cisco_ios_l3_simple_raw", "cisco_ios_l3_simple_parsed"),
    ],
)
def test_cisco_ios_parse_config(raw_config, parsed_config, request):
    raw_config = request.getfixturevalue(raw_config)
    parsed_config = request.getfixturevalue(parsed_config)
    device = CiscoIOSDevice(None)
    device.config = raw_config
    device.parse_config()
    assert device.data == [parsed_config]
