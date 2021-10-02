"""Dataclass objects for faddr's internal usage"""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class IPv4:
    address: str
    mask: str
    attr: List[str] = field(default_factory=list)


@dataclass
class ACL:
    name: str
    direction: str = None
    version: int = "ipv4"


@dataclass
class XConnect:
    neighbour: str
    vcid: int
    description: str = None
    mtu: int = None
    encapsulation: str = None


@dataclass
class Interface:
    name: str
    description: str = None
    ipv4: List[IPv4] = field(default_factory=list)
    mtu: int = None
    vrf: str = None
    acl: List[ACL] = field(default_factory=list)
    shutdown: bin = False
    xconnect: XConnect = None
