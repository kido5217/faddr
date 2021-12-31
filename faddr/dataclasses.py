"""Dataclass objects for faddr's internal usage."""

from typing import List

from pydantic import BaseModel


class IPv4(BaseModel):
    """Simple ipv4 address dataclass"""

    address: str
    mask: str = "255.255.255.255"
    attr: List[str] = []


# TODO: Add support for vlan list, stacking etc.
class Vlan(BaseModel):
    """Vlan dataclass"""

    id: str
    name: str = None
    encapsulation: str = None
    secondary: bool = False


class ACL(BaseModel):
    """ACL dataclass"""

    name: str
    direction: str = None
    version: str = "ipv4"


class XConnect(BaseModel):
    """Xconnect aka l2citcuit dataclass"""

    neighbour: str
    vcid: int
    description: str = None
    mtu: int = None
    encapsulation: str = None


class Interface(BaseModel):
    """Interface dataclass"""

    name: str
    description: str = None
    vlans: List[Vlan] = []
    ipv4: List[IPv4] = []
    mtu: int = None
    vrf: str = None
    acl: List[ACL] = []
    shutdown: bool = False
    xconnect: XConnect = None
