"""Pydantic data schemas."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field, root_validator, validator


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
    acl_in: str = None
    acl_out: str = None
    acls: List[Dict] = []

    sa_mapping: Dict[str, str] = Field(
        {
            "ip_addresses": "IPAddress",
            "acls": "InterfaceACL",
        },
        exclude=True,
    )

    @validator("ip_addresses")
    def dedup_ip(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Delete duplicate ip addresses from interface."""
        ip_addresses = []
        for ip_address in values:
            if ip_address not in ip_addresses:
                ip_addresses.append(ip_address)
        return ip_addresses

    @root_validator(pre=True)
    def acls_to_dicts(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Convert acls lists from parset into single list of dicts."""
        if len(values.get("acls", [])) > 0:
            return values

        acls = []
        directions = ("in", "out")
        for direction in directions:
            container = "acls_" + direction
            if values.get(container) is not None:
                acl_list = values.get(container)
                acl_list = list(acl_list) if isinstance(acl_list, str) else acl_list
                for sequence_number, name in enumerate(acl_list):
                    acl = {
                        "name": name,
                        "sequence_number": sequence_number,
                        "direction": direction,
                    }
                    acls.append(acl)

        if len(acls) > 0:
            values["acls"] = acls

        return values

    @root_validator(pre=True)
    def acls_to_acl_string(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Add acl's from general list into subcategies for easier search."""
        directions = ("in", "out")
        for direction in directions:
            list_key = "acls_" + direction
            key = "acl_" + direction
            if values.get(key) is None and values.get(list_key) is not None:
                values[key] = ", ".join(values.get(list_key))

        return values


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
