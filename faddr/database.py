"""Database operations."""

import ipaddress
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from faddr import logger
from faddr.exceptions import FaddrDatabaseDirError
from faddr.models import Base, Device, Interface, IPAddress, ModelFactory
from faddr.schemas import DeviceSchema


model_factory = ModelFactory()


def make_sa_object(sa_class, data):
    """Create SQLAlchemy table object from provided data."""
    sa_obj_data = {}
    for key in sa_class.__table__.columns.keys():
        sa_obj_data[key] = dict(data).get(key)

    for (relative, sa_subclass_name) in dict(data).get("sa_mapping", {}).items():
        sa_sub_class = model_factory.get(sa_subclass_name)
        # Create one-to-many relatives
        if isinstance(dict(data).get(relative), list):
            sa_obj_data[relative] = []
            for sub in dict(data).get(relative):
                sa_obj_data[relative].append(make_sa_object(sa_sub_class, sub))

    return sa_class(**sa_obj_data)


class Database:
    """Create db, connect to it, modify and search."""

    def __init__(self, path, name, revision=None, revisions=10):
        self.path = Path(path)
        try:
            self.path.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, PermissionError):
            raise FaddrDatabaseDirError(
                self.path, "path isn't a directory or isn't readable or writable."
            ) from None

        self.revisions = revisions
        self.basename = name
        self.revision = revision
        if self.revision is None:
            self.name = name
        else:
            rev_name = Path(self.basename).stem + "-" + self.revision
            suffix = Path(self.basename).suffix
            self.name = rev_name + suffix

        logger.debug(f"Created Database class: {self.__dict__}")

    @property
    def engine(self):
        """Create SQLAlchemy engine."""
        db_file = Path(self.path, self.name)
        # SQLite 'dataabse is locked' workaround for multiprocessing.
        # In the future, when we'll support others DB drivers,
        # using sqlite should imply settings.processes=1 and disable multiprocessing
        connect_args = {"timeout": 300}
        engine = create_engine(
            f"sqlite+pysqlite:///{db_file}",
            future=True,
            connect_args=connect_args,
        )
        return engine

    def new_revision(self, revision=None):
        """Create new revision and IP it."""
        if revision:
            self.revision = revision
        else:
            self.revision = self.gen_revision_id()

        rev_name = Path(self.basename).stem + "-" + self.revision
        suffix = Path(self.basename).suffix
        self.name = rev_name + suffix

        Base.metadata.create_all(self.engine)
        logger.debug(f"Created new revision: '{self.revision}'")

        return self.revision

    def insert_device(self, device_data):
        """Insert device data to database."""

        device = make_sa_object(Device, DeviceSchema.parse_obj(device_data))

        with Session(self.engine) as session:
            session.add(device)
            session.commit()

        logger.debug(f"Inserted device: '{device_data['name']}'")

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

    def cleanup(self):
        """Delete revisions that exceed the maximum number of allowed revisions."""
        if self.revisions == -1:
            logger.debug(
                f"'database.revisions' is '{self.revisions}', keeping all revisions."
            )
            return 0

        revision_list = []
        for revision_candidate in self.path.iterdir():
            if len(revision_candidate.name) == len(self.basename) + 15:
                revision_list.append(revision_candidate)
        revision_list.sort(reverse=True)
        logger.debug(
            f"Found {len(revision_list)} revisions: {[revision.name for revision in revision_list]}"
        )

        if len(revision_list) > self.revisions:
            logger.debug(f"Deleting {len(revision_list) - self.revisions} revisions...")
            for revision_to_delete in revision_list[self.revisions :]:
                revision_to_delete.unlink()
                logger.debug(f"Deleted {revision_to_delete}")
            return len(revision_list) - self.revisions
        return 0

    def find_networks(self, queries):
        """Find provided networks."""

        result = {}

        for query in queries:
            result.update(self.find_network(query))

        return result

    def find_network(self, query):
        """Find provided network."""

        netmask_max = 16
        netmask_min = 32

        logger.debug(f"Searchong for {query}")

        result = {query: []}
        query_addr = query.split("/")[0]

        networks = []
        for netmask in range(netmask_max, netmask_min + 1):
            calculated_network = ipaddress.IPv4Network(
                (query_addr, netmask), strict=False
            ).with_prefixlen
            networks.append(calculated_network)
            logger.debug(f"Added {calculated_network} to search list")

        stmt_direct = (
            select(
                Device.name.label("device"),
                Interface.name.label("interface"),
                IPAddress.with_prefixlen.label("ip_address"),
                Interface.vrf,
                Interface.acl_in,
                Interface.acl_out,
                Interface.is_disabled,
                Interface.description,
            )
            .where(
                IPAddress.network.in_(networks),
                Interface.id == IPAddress.interface_id,
                Device.id == Interface.device_id,
            )
            .order_by(Device.name)
            .order_by(Interface.name)
            .order_by(IPAddress.with_prefixlen)
        )

        with Session(self.engine) as session:
            for row in session.execute(stmt_direct):
                data = dict(row)
                data["type"] = "direct"
                if data not in result[query]:
                    result[query].append(data)
                logger.debug(f"Found address: {data}")

        return result

    @staticmethod
    def gen_revision_id():
        """Generate revision."""
        date_format = "%Y%m%d%H%M%S"
        revision = datetime.now().strftime(date_format)

        return revision
