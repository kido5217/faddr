"""Dataclass objects for faddr's internal usage"""

from dataclasses import dataclass
from typing import List


@dataclass
class IPv4:
    address: str
    mask: str
    attr: List[str]


@dataclass
class Interface:
    name: str
    ipv4: List[IPv4]
    description: str
    mtu: int
