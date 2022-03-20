"""Database operations."""

import ipaddress
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import Session, declarative_base

from faddr import logger
from faddr.exceptions import FaddrDatabaseDirError


Base = declarative_base()


class Device(Base):  # pylint: disable=too-few-public-methods
    """ORM 'device' table data mapping."""

    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    source = Column(String)


class Interface(Base):  # pylint: disable=too-few-public-methods
    """ORM 'interface' table data mapping."""

    __tablename__ = "interface"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_interface = Column(String)
    unit = Column(String)
    duplex = Column(String)
    speed = Column(String)
    description = Column(String)
    is_disabled = Column(Boolean, default=False)
    encapsulation = Column(String)
    s_vlan = Column(Integer)
    c_vlan = Column(Integer)
    vrf = Column(String)
    acl_in = Column(String)
    acl_out = Column(String)

    device_id = Column(Integer, ForeignKey("device.id"))


class IP(Base):  # pylint: disable=too-few-public-methods
    """ORM 'ip' table data mapping."""

    __tablename__ = "ip"

    id = Column(Integer, primary_key=True)
    broadcast_address = Column(String)
    compressed = Column(String)
    exploded = Column(String)
    hostmask = Column(String)
    hosts = Column(Integer)
    ip = Column(String)
    is_link_local = Column(Boolean, default=False)
    is_loopback = Column(Boolean, default=False)
    is_multicast = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    is_reserved = Column(Boolean, default=False)
    is_unspecified = Column(Boolean, default=False)
    max_prefixlen = Column(Integer)
    netmask = Column(String)
    network = Column(String)
    network_address = Column(String)
    num_addresses = Column(Integer)
    prefixlen = Column(Integer)
    version = Column(Integer)
    with_hostmask = Column(String)
    with_netmask = Column(String)
    with_prefixlen = Column(String)

    interface_id = Column(Integer, ForeignKey("interface.id"))


class Database:
    """Create db, connect to it, modify and search."""

    def __init__(self, path, name):
        self.path = Path(path)
        if not self.path.exists():
            raise FaddrDatabaseDirError(
                self.path, "path doesn't exist or isn't readable"
            )
        if not self.path.is_dir():
            raise FaddrDatabaseDirError(self.path, "path isn't a directory")

        self.basename = name
        self.name = name
        self.revision = None
        logger.debug(f"Created Database class: {self.__dict__}")

    @property
    def engine(self):
        """Create SQLAlchemy engine."""
        db_file = Path(self.path, self.name)
        engine = create_engine(f"sqlite+pysqlite:///{db_file}", future=True)
        return engine

    def new(self, revision=None):
        """Create new revision and return it."""
        if revision:
            self.revision = revision
        else:
            self.revision = self.gen_revision()

        rev_name = Path(self.basename).stem + "-" + self.revision
        suffix = Path(self.basename).suffix
        self.name = rev_name + suffix

        Base.metadata.create_all(self.engine)
        logger.debug(f"Created new revision: '{self.revision}'")

        return self.revision

    def insert_device(self, device_data):
        """Insert device data to database."""

        device = Device(**device_data["info"])

        with Session(self.engine) as session:
            session.add(device)
            session.commit()
            device_id = device.id

        for interface_name, interface_data in device_data.get("interfaces", {}).items():
            self.insert_interface(device_id, interface_name, interface_data)

        logger.debug(f"Inserted device: '{device_data['info']}'")

    def insert_interface(self, device_id, name, data):
        """Insert interface data to database."""

        table_data = {}
        for key in Interface.__table__.columns.keys():
            table_data[key] = data.get(key)
        table_data["name"] = name
        table_data["device_id"] = device_id

        interface = Interface(**table_data)

        with Session(self.engine) as session:
            session.add(interface)
            session.commit()
            interface_id = interface.id

        for ip_address in data.get("ip", []):
            self.insert_ip_address(interface_id, ip_address)

        logger.debug(f"Interted interface {data}")

    def insert_ip_address(self, interface_id, data):
        """Insert ip_address data to database."""

        table_data = {}
        for key in IP.__table__.columns.keys():
            table_data[key] = data.get(key)
        table_data["interface_id"] = interface_id

        ip_address = IP(**table_data)

        with Session(self.engine) as session:
            session.add(ip_address)
            session.commit()

        logger.debug(f"Inserted IP address {data}")

    def get_devices(self):
        """Get device list from database."""

        with Session(self.engine) as session:
            return session.query(Device).all()

    def set_default(self):
        """Make current revision default one."""
        if self.name != self.basename:
            base_file = Path(self.path, self.basename)
            rev_file = Path(self.path, self.name)
            if base_file.exists():
                base_file.unlink()
            base_file.symlink_to(rev_file)
            self.name = self.basename
            logger.debug(f"Created symlink '{base_file}' to '{rev_file}'")

    def is_default(self):
        """Check if current revision is default."""
        return self.name == self.basename

    def find_network(self, network, netmask_min=32, netmask_max=24):
        """Find provided netwkork."""

        logger.debug(f"Searchong for {network}")
        result = {
            "header": [
                "Device",
                "Interface",
                "IP",
                "VRF",
                "ACL in",
                "ACL out",
                "Shutdown",
                "Description",
            ],
            "data": [],
        }

        networks = []
        for netmask in range(netmask_max, netmask_min + 1):
            calculated_network = ipaddress.IPv4Network(
                (network.split("/")[0], netmask), strict=False
            ).with_prefixlen
            networks.append(calculated_network)
            logger.debug(f"Added {calculated_network} to search list")

        stmt = (
            select(
                Device.name.label("device"),
                Interface.name.label("interface"),
                IP.with_prefixlen,
                Interface.vrf,
                Interface.acl_in,
                Interface.acl_out,
                Interface.is_disabled,
                Interface.description,
            )
            .where(
                IP.network.in_(networks),
                Interface.id == IP.interface_id,
                Device.id == Interface.device_id,
            )
            .order_by(Device.name)
            .order_by(Interface.name)
            .order_by(IP.with_prefixlen)
        )

        with Session(self.engine) as session:
            for row in session.execute(stmt):
                data = dict(zip(result["header"], row))
                result["data"].append(data)
                logger.debug(f"Found address: {data}")

        return result

    @staticmethod
    def gen_revision():
        """Generate revision."""
        date_format = "%Y%m%d%H%M%S"
        revision = datetime.now().strftime(date_format)

        return revision
