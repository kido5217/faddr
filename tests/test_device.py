import pytest

from faddr import Device, CiscoIOSDevice


def test_device_factory():
    assert isinstance(Device(None, device_type="cisco"), CiscoIOSDevice)
    assert isinstance(Device(None, device_type="cisco_ios"), CiscoIOSDevice)


@pytest.mark.skip(reason="WIP")
def test_ciscoios_read_config():
    device = CiscoIOSDevice(None)
