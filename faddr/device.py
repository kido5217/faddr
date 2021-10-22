"""Read, sanitize and parse network devices' configuration."""

import dataclasses
import re

from ciscoconfparse import CiscoConfParse

from faddr.dataclasses import Interface, IPv4, ACL, Vlan, XConnect
from faddr.exceptions import FaddrDeviceUnsupportedType


class CiscoIOSDevice:
    """Load, sanitize and parse Cisco IOS configuration files."""

    regex_intf = re.compile(r"^interface")
    regex_intf_name = re.compile(r"^interface\s+(\S.+?)$")

    regex_intf_descr = re.compile(r"description\s(\S+)")
    regex_vlan = re.compile(r"encapsulation\s(\S+)\s(\d+)")
    regex_ipv4 = re.compile(r"ip\saddress\s(\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+)")
    regex_vrf = re.compile(r"vrf\sforwarding\s(\S+)")
    regex_ipv4_acl = re.compile(r"ip\saccess-group\s(\S+)\s(in|out)")
    regex_shutdown = re.compile(r"^ shutdown$")
    regex_mtu = re.compile(r"mtu\s(\d+)")
    regex_xconnect = re.compile(r"xconnect\s(\S+)\s(\S+)\sencapsulation\s(\S+)")

    # TODO: make loading from file optional, add reading from variable
    def __init__(self, config_path, device_type="cisco_ios"):
        """Read device's raw configuration and sanitize it."""
        self.device_type = device_type
        self.config_path = config_path
        self.data = None

    def read_config(self):
        """Read config from file."""
        # Set "errors" to "ignore" to ignore mangled utf8 in junos and huawey configs
        with open(
            self.config_path, mode="r", errors="ignore", encoding="ascii"
        ) as config_file:
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

    def __parse_interface(self, interface):
        intf_data = Interface(interface.re_match_typed(self.regex_intf_name))

        # Get description
        intf_descr = interface.re_search_children(self.regex_intf_descr)
        if len(intf_descr) > 0:
            _, description = intf_descr[0].text.strip().split(" ", 1)
            intf_data.description = description

        # Get vlan
        intf_vlan = interface.re_search_children(self.regex_vlan)
        if len(intf_vlan) > 0:
            vlan_arr = intf_vlan[0].text.strip().split()
            vlan = Vlan(vlan_arr[2], encapsulation=vlan_arr[1])
            intf_data.vlans.append(vlan)
            if len(vlan_arr) == 5:
                second_vlan = Vlan(
                    vlan_arr[4], encapsulation=vlan_arr[1], secondary=True
                )
                intf_data.vlans.append(second_vlan)

        # Get ipv4 addresses
        intf_ip_addrs = interface.re_search_children(self.regex_ipv4)
        if len(intf_ip_addrs) > 0:
            for intf_ip_addr in intf_ip_addrs:
                ipaddr = intf_ip_addr.text.strip().split()
                # TODO: log if len isn't 4 or 5
                if len(ipaddr) == 4:
                    ipv4 = IPv4(ipaddr[2], mask=ipaddr[3])
                    intf_data.ipv4.append(ipv4)
                elif len(ipaddr) == 5:
                    ipv4 = IPv4(ipaddr[2], mask=ipaddr[3], attr=[ipaddr[4]])
                    intf_data.ipv4.append(ipv4)

        # Get VRF name
        intf_vrf = interface.re_search_children(self.regex_vrf)
        if len(intf_vrf) > 0:
            _, _, _, vrf_name = intf_vrf[0].text.strip().split()
            intf_data.vrf = vrf_name

        # Get ACL
        intf_acls = interface.re_search_children(self.regex_ipv4_acl)
        if len(intf_acls) > 0:
            for intf_acl in intf_acls:
                _, _, acl_name, direction = intf_acl.text.strip().split()
                acl = ACL(acl_name, direction=direction)
                intf_data.acl.append(acl)

        # Check if shutdown command present
        intf_shutdown = interface.re_search_children(self.regex_shutdown)
        if len(intf_shutdown) > 0:
            intf_data.shutdown = True

        # Get XC configuration
        intf_xc = interface.re_search_children(self.regex_xconnect)
        if len(intf_xc) > 0:
            xc_data = intf_xc[0].text.strip().split()
            xc = XConnect(xc_data[1], int(xc_data[2]), encapsulation=xc_data[4])

            # Get additional XC params
            intf_xc_mtu = intf_xc[0].re_search_children(self.regex_mtu)
            if len(intf_xc_mtu) > 0:
                _, xc_mtu = intf_xc_mtu[0].text.strip().split()
                xc.mtu = int(xc_mtu)

            intf_data.xconnect = xc

        return intf_data

    def parse_config(self):
        """Get device's interfaces and their configuration."""
        dev_data = []

        parser = self.__get_parser()

        # Find all interfaces
        for interface in parser.find_objects(self.regex_intf):
            dev_data.append(dataclasses.asdict(self.__parse_interface(interface)))

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
