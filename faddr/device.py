import ipaddress
import re

from ciscoconfparse import CiscoConfParse


class Device:
    def __init__(self, config_path, device_type="guess"):
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
        data = {}

        regex_ipv4 = re.compile(
            r"ip\saddress\s(\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+)"
        )
        regex_vrf = re.compile(r"vrf\sforwarding\s(\S+)")

        parse = CiscoConfParse(self.config, syntax="ios")
        for intf_obj in parse.find_objects("^interface"):
            intf_name = intf_obj.re_match_typed("^interface\s+(\S.+?)$")
            data[intf_name] = {}

            intf_ip_addrs = intf_obj.re_search_children(regex_ipv4)
            if len(intf_ip_addrs) > 0:
                for intf_ip_addr in intf_ip_addrs:
                    _, _, ipaddr, mask = intf_ip_addr.text.strip().split()
                    print(ipaddr, mask)

            intf_vrf = intf_obj.re_search_children(regex_vrf)
            if len(intf_vrf) > 0:
                _, _, vrf = intf_vrf[0].text.strip().split()
                print(vrf)

        print(data)
