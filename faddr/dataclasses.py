"""Dataclasses for serializing/deserializing device data."""

from typing import Any, ClassVar, Dict, List
from pydantic import BaseModel, validator

from faddr.database import Interface, IPAddress


class InterfaceModel(BaseModel):
    """Interface data container."""

    _mapping: ClassVar[Dict[str, Any]] = {"ip_address": IPAddress}

    name: str
    ip_address: List[Dict] = []
    parent_interface: str = None
    unit: str = None
    duplex: str = None
    speed: str = None
    description: str = None
    is_disabled: str = None
    encapsulation: str = None
    s_vlan: str = None
    c_vlan: str = None
    vrf: str = None
    # acl_in: List[str] = []
    # acl_out: List[str] = []


class DeviceModel(BaseModel):
    """Device root data container."""

    _mapping: ClassVar[Dict[str, Any]] = {"interfaces": Interface}

    name: str
    path: str = None
    source: str = None
    interfaces: List[InterfaceModel] = []

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
