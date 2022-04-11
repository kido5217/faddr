"""SQLAlchemy data models."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Device(Base):  # pylint: disable=too-few-public-methods
    """ORM 'device' table data mapping."""

    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    path = Column(String)
    source = Column(String)

    interfaces = relationship("Interface", back_populates="device")


class Interface(Base):  # pylint: disable=too-few-public-methods
    """ORM 'interface' table data mapping."""

    __tablename__ = "interface"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    parent_interface = Column(String)
    unit = Column(String)
    duplex = Column(String)
    speed = Column(String)
    description = Column(String, index=True)
    is_disabled = Column(Boolean, default=False)
    encapsulation = Column(String)
    s_vlan = Column(Integer)
    c_vlan = Column(Integer)
    vrf = Column(String, index=True)
    acl_in = Column(String, index=True)
    acl_out = Column(String, index=True)

    device_id = Column(Integer, ForeignKey("device.id"))
    device = relationship("Device", back_populates="interfaces")

    ip_addresses = relationship("IPAddress", back_populates="interface")


class IPAddress(Base):  # pylint: disable=too-few-public-methods
    """ORM 'ip' table data mapping."""

    __tablename__ = "ip"

    id = Column(Integer, primary_key=True)
    broadcast_address = Column(String)
    compressed = Column(String)
    exploded = Column(String)
    hostmask = Column(String)
    hosts = Column(Integer)
    ip = Column(String, index=True)
    is_link_local = Column(Boolean, default=False)
    is_loopback = Column(Boolean, default=False)
    is_multicast = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    is_reserved = Column(Boolean, default=False)
    is_unspecified = Column(Boolean, default=False)
    max_prefixlen = Column(Integer)
    netmask = Column(String)
    network = Column(String, index=True)
    network_address = Column(String, index=True)
    num_addresses = Column(Integer)
    prefixlen = Column(Integer)
    version = Column(Integer)
    with_hostmask = Column(String)
    with_netmask = Column(String)
    with_prefixlen = Column(String)

    interface_id = Column(Integer, ForeignKey("interface.id"))
    interface = relationship("Interface", back_populates="ip_addresses")


class ModelFactory:  # pylint: disable=too-few-public-methods
    """Factory for SQLAlchemy class generation."""

    @staticmethod
    def get(class_name):
        """Get class from current submodule."""
        return globals()[class_name]
