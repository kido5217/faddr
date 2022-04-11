"""Pydantic data schemas."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator


class Result(BaseModel):
    """Network search result."""

    headers: Dict[str, List[str]] = {
        "full": [
            "Query",
            "Device",
            "Interface",
            "IP",
            "VRF",
            "ACL in",
            "ACL out",
            "Shutdown",
            "Description",
        ]
    }
    data: List[Dict] = []


class InterfaceSchema(BaseModel):
    """Interface data container."""

    name: str
    ip_addresses: List[Dict] = []
    parent_interface: str = None
    unit: str = None
    duplex: str = None
    speed: str = None
    description: str = None
    is_disabled: bool = None
    encapsulation: str = None
    s_vlan: str = None
    c_vlan: str = None
    vrf: str = None
    # acl_in: List[str] = []
    # acl_out: List[str] = []

    sa_mapping: Dict[str, Any] = Field({"ip_addresses": "IPAddress"}, exclude=True)

    @validator("ip_addresses")
    def dedup_ip(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Delete duplicate ip addresses from interface."""
        ip_addresses = []
        for ip_address in values:
            if ip_address not in ip_addresses:
                ip_addresses.append(ip_address)
        return ip_addresses


class DeviceSchema(BaseModel):
    """Device root data container."""

    name: str = None
    path: str = None
    source: str = None
    interfaces: List[InterfaceSchema] = []

    sa_mapping: Dict[str, Any] = Field({"interfaces": "Interface"}, exclude=True)

    @validator("interfaces", pre=True)
    def flatten_interfaces(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Convert dict of interfaces to list of dicts."""
        if isinstance(values, Dict):
            interfaces = []
            for name, data in values.items():
                data["name"] = name
                interfaces.append(data)
            return interfaces
        return values
