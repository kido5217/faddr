"""Dataclasses for serializing/deserializing device data."""


from typing import Dict, List

from pydantic import BaseModel


class InterfaceModel(BaseModel):
    """Interface data container."""

    name: str
    ip: List[Dict] = []
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
    acl_in: List[Dict] = []
    acl_out: List[Dict] = []


class DeviceModel(BaseModel):
    """Device root data container."""

    name: str
    path: str = None
    source: str = None
    interfaces: List[InterfaceModel] = []
