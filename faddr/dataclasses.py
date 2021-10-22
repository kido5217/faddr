"""Dataclass objects for faddr's internal usage."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class IPv4:
    """Simple ipv4 address dataclass"""

    address: str
    mask: str = "255.255.255.255"
    attr: List[str] = field(default_factory=list)


# TODO: Add support for vlan list, stacking etc.
@dataclass
class Vlan:
    """Vlan dataclass"""

    id: str
    name: str = None
    encapsulation: str = None
    secondary: bin = False


@dataclass
class ACL:
    """ACL dataclass"""

    name: str
    direction: str = None
    version: str = "ipv4"


@dataclass
class XConnect:
    """Xconnect aka l2citcuit dataclass"""

    neighbour: str
    vcid: int
    description: str = None
    mtu: int = None
    encapsulation: str = None


@dataclass
class Interface:
    """Interface dataclass"""

    name: str
    description: str = None
    vlans: List[Vlan] = field(default_factory=list)
    ipv4: List[IPv4] = field(default_factory=list)
    mtu: int = None
    vrf: str = None
    acl: List[ACL] = field(default_factory=list)
    shutdown: bin = False
    xconnect: XConnect = None
