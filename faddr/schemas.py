"""Pydantic data schemas."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field, root_validator, validator


class Result(BaseModel):
    """Network search result."""

    headers: Dict[str, List[str]] = {
        "full": [
            "Query",
            "Device",
            "Interface",
            "IP",
            "VRF",
            # "ACL in",
            # "ACL out",
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
    def acls_to_lists(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Convert single asls to lists"""
        for acl_container in ("acls_in", "acls_out"):
            acls = values.get(acl_container, [])
            if isinstance(acls, str):
                acls = [acls]
            elif not isinstance(acls, list):
                raise ValueError("must be str or list")
            if len(acls) > 0:
                values[acl_container] = acls

        return values

    @root_validator(pre=True)
    def unpack_acls(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """combine acls_in and acls_out into 'acls' list of dicts."""
        acls = values.get("acls", [])
        if acls is None:
            acls = []

        acls_data = {
            "acls_in": values.get("acls_in"),
            "acls_out": values.get("acls_out"),
        }
        for direction_key, acl_data in acls_data.items():
            if acl_data is None:
                continue

            direction = "in" if direction_key == "acls_in" else "out"

            for sequence_number, acl in enumerate(acl_data):
                if isinstance(acl, str):
                    acl = {
                        "name": acl,
                        "sequence_number": sequence_number,
                        "direction": direction,
                    }
                elif isinstance(acl, dict):
                    acl["sequence_number"] = sequence_number
                    acl["direction"] = direction
                else:
                    raise ValueError("must be str or dict")
                acls.append(acl)

        if len(acls) > 0:
            values["acls"] = acls

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
