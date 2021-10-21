import pathlib
import re
import traceback

from faddr.device import Device


class RancidDir:
    def __init__(self, rancid_path):
        """Open rancid dir and parse it's content."""
        self.path = pathlib.Path(rancid_path)

    def is_valid(self):
        is_valid = False
        if self.path.exists():
            for child in self.path.iterdir():
                if child.is_dir() and (child / "router.db").exists():
                    is_valid = True
        return is_valid

    def load_groups(self, rancid_groups=None):
        groups = []
        for child in self.path.iterdir():
            if child.is_dir() and (child / "router.db").exists():
                groups.append(child.name)

        if rancid_groups is not None:
            requested_groups = re.split("[,|; ]", rancid_groups)
            filtered_groups = []
            for group in groups:
                if group in requested_groups:
                    filtered_groups.append(group)
            groups = filtered_groups

        return groups

    def parse_configs(self, group):
        devices = {}
        data = {}

        try:
            with open(self.path / group / "router.db", mode="r") as router_db:
                devices_list = router_db.readlines()
        except Exception:
            return {}

        for line in devices_list:
            if len(line.strip()) == 0:
                continue
            # TODO: Add ipv6 support
            device_data = re.split("[;:]", line.strip())
            if len(device_data) < 3:
                continue
            elif device_data[0].startswith("#"):
                continue
            elif device_data[2] != "up":
                continue
            else:
                devices[device_data[0]] = device_data[1]

        for device_name, device_type in devices.items():
            config_path = self.path / group / "configs" / device_name
            try:
                device = Device(config_path, device_type=device_type)
                device.read_config()
                device.parse_config()
            # TODO: Use custom Exception
            except ValueError:
                traceback.print_exc()
            data[device_name] = device.data

        return data
