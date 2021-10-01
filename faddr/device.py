"""Read, sanitize and parse network devices' configuration."""

import ipaddress
import re

from ciscoconfparse import CiscoConfParse


def calculate_net(ipaddr, mask):
    try:
        network = ipaddress.ip_network((ipaddr + "/" + mask), strict=False)
    except Exception:
        return {}
    return str(network)


class CiscoIOSDevice:
    """Load, sanitize and parse Cisco IOS configuration files"""

    # TODO: make loading from file optional, add reading from variable
    def __init__(self, config_path, device_type="cisco_ios"):
        """Read device's raw configuration and sanitize it."""
        self.device_type = device_type
        self.config_path = config_path
        self.data = None

    def read_config(self):
        # Set "errors" to "ignore" to ignore mangled utf8 in junos and huawey configs
        with open(self.config_path, mode="r", errors="ignore") as config_file:
            self.raw_config = config_file.readlines()

        self.config = self.sanitize_config()

    def sanitize_config(self):
        config = []
        for line in self.raw_config:
            line = line.rstrip()
            if line.startswith("!") is False:
                config.append(line)
        return config

    def parse_config(self):
        """Get device's interfaces and their configuration."""
        data = {}

        regex_ipv4 = re.compile(
            r"ip\saddress\s(\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+)"
        )
        regex_vrf = re.compile(r"vrf\sforwarding\s(\S+)")

        parse = CiscoConfParse(self.config, syntax="ios")

        # TODO: Use dataclasses
        # Find all interfaces
        for intf_obj in parse.find_objects(r"^interface"):
            intf_name = intf_obj.re_match_typed(r"^interface\s+(\S.+?)$")

            # Get L3 interface data
            intf_ip_addrs = intf_obj.re_search_children(regex_ipv4)
            if len(intf_ip_addrs) > 0:
                data[intf_name] = {}
                # Get ipv4 addressrs
                for intf_ip_addr in intf_ip_addrs:
                    _, _, ipaddr, mask = intf_ip_addr.text.strip().split()
                    # I don't like this, need to change
                    data[intf_name][calculate_net(ipaddr, mask)] = ipaddr + "/" + mask
                # Get VRF name
                intf_vrf = intf_obj.re_search_children(regex_vrf)
                if len(intf_vrf) > 0:
                    _, _, vrf = intf_vrf[0].text.strip().split()
                    data[intf_name]["vrf"] = vrf

        self.data = data


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
        raise ValueError(
            "Unsupported 'device_type' "
            f"currently supported platforms are: {str(CLASS_MAPPER)}"
        )
    DeviceClass = CLASS_MAPPER[device_type]
    return DeviceClass(*args, **kwargs)
