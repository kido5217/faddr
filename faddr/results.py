"""Classes for de/serializing and printing search results."""


class NetworkResult:
    """Process network search results."""

    schema = {
        "headers": {
            "direct": (
                "Query",
                "Device",
                "Interface",
                "IP",
                "VRF",
                "ACL in",
                "ACL out",
                "Shutdown",
                "Description",
            ),
            "static": (
                "Query",
                "Device",
                "Interface",
                "Network",
                "VRF",
                "Nexthop",
                "Name",
            ),
        },
        "keys": {
            "direct": (
                "query",
                "device",
                "interface",
                "ip_address",
                "vrf",
                "acl_in",
                "acl_out",
                "is_disabled",
                "description",
            ),
            "static": (
                "query",
                "device",
                "interface",
                "network",
                "vrf",
                "nexthop",
                "name",
            ),
        },
        "tables": ("direct", "static"),
    }

    def __init__(self, data):
        self.data = data
        self.tables = None
