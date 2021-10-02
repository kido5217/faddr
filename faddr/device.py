"""Read, sanitize and parse network devices' configuration."""

import ipaddress
import re

from ciscoconfparse import CiscoConfParse

from faddr.exceptions import FaddrDeviceUnsupportedType


def calculate_net(ipaddr, mask):
    try:
        network = ipaddress.ip_network((ipaddr + "/" + mask), strict=False)
    except Exception:
        return {}
    return str(network)


class CiscoIOSDevice:
    """Load, sanitize and parse Cisco IOS configuration files"""

    regex_intf = re.compile(r"^interface")
    regex_intf_name = re.compile(r"^interface\s+(\S.+?)$")

    regex_ipv4 = re.compile(r"ip\saddress\s(\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+)")
    regex_vrf = re.compile(r"vrf\sforwarding\s(\S+)")

    # TODO: make loading from file optional, add reading from variable
    def __init__(self, config_path, device_type="cisco_ios"):
        """Read device's raw configuration and sanitize it."""
        self.device_type = device_type
        self.config_path = config_path
        self.data = None

    def read_config(self):
        """Read config from file."""
        # Set "errors" to "ignore" to ignore mangled utf8 in junos and huawey configs
        with open(self.config_path, mode="r", errors="ignore") as config_file:
            self.raw_config = config_file.readlines()

        self.config = self.sanitize_config()

    def sanitize_config(self):
        """Delete empty and comment strings and garbage."""
        config = []
        for line in self.raw_config:
            line = line.rstrip()
            if line.startswith("!") is False:
                config.append(line)
        return config

    def __get_parser(self):
        return CiscoConfParse(self.config, syntax="ios")

    def __get_interfaces(self, parser):
        return parser.find_objects(self.regex_intf)

    def __parse_interface(self, interface):
        pass

    def parse_config(self):
        """Get device's interfaces and their configuration."""

        dev_data = {}

        parser = self.__get_parser()

        # TODO: Use dataclasses
        # Find all interfaces
        for interface in self.__get_interfaces(parser):
            intf_name = interface.re_match_typed(self.regex_intf_name)
            dev_data[intf_name] = self.__parse_interface(interface)

            # Get L3 interface data
            intf_ip_addrs = interface.re_search_children(self.regex_ipv4)
            if len(intf_ip_addrs) > 0:
                dev_data[intf_name] = {}
                # Get ipv4 addressrs
                for intf_ip_addr in intf_ip_addrs:
                    _, _, ipaddr, mask = intf_ip_addr.text.strip().split()
                    # I don't like this, need to change
                    dev_data[intf_name][calculate_net(ipaddr, mask)] = (
                        ipaddr + "/" + mask
                    )
                # Get VRF name
                intf_vrf = interface.re_search_children(self.regex_vrf)
                if len(intf_vrf) > 0:
                    _, _, vrf = intf_vrf[0].text.strip().split()
                    dev_data[intf_name]["vrf"] = vrf

        if len(dev_data) > 0:
            self.data = dev_data


# Map device_type value to real device Class
CLASS_MAPPER = {
    "cisco": CiscoIOSDevice,
    "cisco_ios": CiscoIOSDevice,
}


def Device(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type."""
    device_type = kwargs["device_type"]
    if device_type not in CLASS_MAPPER:
        # TODO: Use custom Exception
        raise FaddrDeviceUnsupportedType(
            "Unsupported 'device_type' "
            f"currently supported platforms are: {str(CLASS_MAPPER)}"
        )
    DeviceClass = CLASS_MAPPER[device_type]
    return DeviceClass(*args, **kwargs)
