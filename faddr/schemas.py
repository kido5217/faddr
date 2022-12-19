"""Pydantic data schemas."""

from ipaddress import ip_interface
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, root_validator, validator


class InterfaceSchema(BaseModel):
    """Interface data container."""

    name: str
    ip_addresses: List[Dict] = []
    parent_interface: Union[str, None] = None
    unit: Union[str, None] = None
    duplex: Union[str, None] = None
    speed: Union[str, None] = None
    description: Union[str, None] = None
    is_disabled: bool = False
    encapsulation: Union[str, None] = None
    s_vlan: Union[str, None] = None
    c_vlan: Union[str, None] = None
    vrf: Union[str, None] = None
    acl_in: Union[str, None] = None
    acl_out: Union[str, None] = None
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


class StaticRouteSchema(BaseModel):
    """Static route data container."""

    network: str
    vrf: Union[str, None] = None
    interface: Union[str, None] = None
    nexthop: Union[str, None] = None
    ad: Union[str, None] = None
    name: Union[str, None] = None

    #    @root_validator(pre=True)
    #    def flatten_vrf(cls, values):  # pylint: disable=no-self-argument,no-self-use
    #        """Convert dict of dicts to dict."""
    #
    #        if len(values.keys()) == 1:
    #            print(values)
    #            new_values = list(values.values())[0]
    #            new_values["vrf"] = list(values.keys())[0]
    #            return new_values
    #        return values

    @root_validator(pre=True)
    def separate_nexthop_and_interface(
        cls, values
    ):  # pylint: disable=no-self-argument,no-self-use
        """Separate nexthop and interface."""

        nexthop_or_interface = values.get("nexthop_or_interface")
        if nexthop_or_interface is not None:
            try:
                ip_interface(nexthop_or_interface)
                values["nexthop"] = nexthop_or_interface
            except ValueError:
                values["interface"] = nexthop_or_interface
            del values["nexthop_or_interface"]
        return values


class DeviceSchema(BaseModel):
    """Device root data container."""

    name: Union[str, None] = None
    path: Union[str, None] = None
    source: Union[str, None] = None
    interfaces: List[InterfaceSchema] = []
    static_routes: List[StaticRouteSchema] = []

    sa_mapping: Dict[str, Any] = Field(
        {
            "interfaces": "Interface",
            "static_routes": "StaticRoute",
        },
        exclude=True,
    )

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


class APINetworkQueryBody(BaseModel):
    """REST API network search request."""

    networks: List[str]

    @validator("networks")
    def is_ip(value):  # pylint: disable=no-self-argument,no-self-use
        """Check if value is valid ip address or network."""
        for network in value:
            ip_interface(network)
        return value


class RevisionSchema(BaseModel):
    """Revision DB search result."""

    id: int
    created: str
    is_active: bool = False

    class Config:
        """Pydantic config."""

        # Enable parsing SQLAlchemy objects
        orm_mode = True
