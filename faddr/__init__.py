"""Parse network devices' configuration and store in database."""

from faddr.rancid import RancidDir
from faddr.device import Device
from faddr.device import CiscoIOSDevice


__version__ = "0.1.0"
__all__ = (
    "RancidDir",
    "Device",
    "CiscoIOSDevice",
)
