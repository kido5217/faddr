"""Dataclass objects for faddr's internal usage"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class IPv4:
    address: str
    mask: str
    attr: List[str] = field(default_factory=list)


@dataclass
class Interface:
    name: str
    description: str = None
    ipv4: List[IPv4] = field(default_factory=list)
    mtu: int = None
    vrf: str = None
