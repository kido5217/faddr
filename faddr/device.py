"""Parse network devices' configuration"""

import ipaddress
import re

from ciscoconfparse import CiscoConfParse


class Device:
    def __init__(self, config_path, device_type="guess"):
        """Read device's raw configuration and sanitize it"""
        # Set "errors" to "ignore" to ignore mangled utf8 in junos and huawey configs
        with open(config_path, mode="r", errors="ignore") as config_file:
            self.raw_config = config_file.readlines()

        if device_type == "guess":
            # TODO: make "guess" function
            pass
        else:
            self.device_type = device_type

        self.config = self.sanitize_config()

    def sanitize_config(self):
        if self.device_type == "cisco":
            config = self.sanitize_config_ios()
        return config

    def sanitize_config_ios(self):
        config = []
        for line in self.raw_config:
            line = line.rstrip()
            if line.startswith("!") is False:
                config.append(line)
        return config

    def parse_config(self):
        if self.device_type == "cisco":
            data = self.parse_config_ios()
        return data

    # TODO: separate different dev types to different subclasses
    def parse_config_ios(self):
        """
        Get device's interfaces and their configuration
        """
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
                    data[intf_name][self.__calculate_net(ipaddr, mask)] = (
                        ipaddr + "/" + mask
                    )
                # Get VRF name
                intf_vrf = intf_obj.re_search_children(regex_vrf)
                if len(intf_vrf) > 0:
                    _, _, vrf = intf_vrf[0].text.strip().split()
                    data[intf_name]["vrf"] = vrf

        return data

    def __calculate_net(self, ipaddr, mask):
        try:
            network = ipaddress.ip_network((ipaddr + "/" + mask), strict=False)
        except Exception:
            return {}
        return str(network)
