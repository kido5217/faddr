"""Database operations."""

import ipaddress

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, Session

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
    duplex = Column(String)
    speed = Column(String)
    description = Column(String)
    disabled = Column(Boolean, default=False)
    encapsulation = Column(String)
    s_vlan = Column(Integer)
    c_vlan = Column(Integer)
    vrf = Column(String)
    acl_in = Column(String)
    acl_out = Column(String)

    device_id = Column(Integer, ForeignKey("device.id"))


class InterfaceIPv4(Base):  # pylint: disable=too-few-public-methods
    """ORM 'ipv4' table data mapping."""

    __tablename__ = "interface_ipv4"

    id = Column(Integer, primary_key=True)
    network = Column(String)
    address = Column(String)
    ip = Column(String)
    mask = Column(String)
    prefixlen = Column(Integer)
    network_address = Column(String)

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

        return self.revision

    def insert_device(self, device_data):
        """Insert device data to database."""

        device = Device(**device_data["info"])

        with Session(self.engine) as session:
            session.add(device)
            session.commit()
            device_id = device.id

        for interface in device_data.get("interfaces", []):
            self.insert_interface(device_id, interface)

    def insert_interface(self, device_id, interface_data):
        """Insert interface data to database."""

        table_data = {}
        for key in Interface.__table__.columns.keys():
            table_data[key] = interface_data.get(key)
        table_data["device_id"] = device_id

        interface = Interface(**table_data)

        with Session(self.engine) as session:
            session.add(interface)
            session.commit()
            interface_id = interface.id

        for ipv4 in interface_data.get("ipv4", []):
            self.insert_ipv4(interface_id, ipv4)

    def insert_ipv4(self, interface_id, ipv4_data):
        """Insert ipv4 data to database."""

        table_data = {}
        for key in InterfaceIPv4.__table__.columns.keys():
            table_data[key] = ipv4_data.get(key)
        table_data["interface_id"] = interface_id

        ipv4 = InterfaceIPv4(**table_data)

        with Session(self.engine) as session:
            session.add(ipv4)
            session.commit()

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

    def is_default(self):
        """Check if current revision is default."""
        return self.name == self.basename

    def find_network(self, network, mask_min=32, mask_max=24):
        """Find provided netwkork."""

        result = {
            "header": (
                "Device",
                "Interface",
                "Shutdown",
                "IP",
                "ACL in",
                "ACL out",
                "Description",
            ),
            "data": [],
        }

        for mask in range(mask_max, mask_min + 1):

            network = ipaddress.ip_network(
                (network.split("/")[0], mask), strict=False
            ).with_prefixlen

            stmt = select(
                Device.name.label("device"),
                Interface.name.label("interface"),
                Interface.disabled,
                InterfaceIPv4.address,
                Interface.acl_in,
                Interface.acl_out,
                Interface.description,
            ).where(
                InterfaceIPv4.network == network,
                Interface.id == InterfaceIPv4.interface_id,
                Device.id == Interface.device_id,
            )

            with Session(self.engine) as session:
                for row in session.execute(stmt):
                    data = dict(zip(result["header"], row))
                    result["data"].append(data)

        return result

    @staticmethod
    def gen_revision():
        """Generate revision."""
        date_format = "%Y%m%d%H%M%S"
        revision = datetime.now().strftime(date_format)

        return revision
