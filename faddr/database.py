"""Database operations."""

import ipaddress
from pathlib import Path

from sqlalchemy import create_engine, event, delete, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from faddr.exceptions import (
    FaddrDatabaseDirError,
    FaddrDatabaseMultipleRevisionsActive,
    FaddrDatabaseNoRevisionsActive,
)
from faddr.logging import logger
from faddr.models import Base, Revision, Device, Interface, IPAddress, ModelFactory
from faddr.schemas import DeviceSchema, RevisionSchema

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

    def __init__(self, path, name, revision_limit=10, init=False):
        self.path = Path(path)
        try:
            self.path.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, PermissionError):
            raise FaddrDatabaseDirError(
                self.path, "path isn't a directory or isn't readable or writable."
            ) from None

        self.revision_limit = revision_limit
        self.name = name
        self.revision_id = None
        self.db_type = "sqlite"

        if init is True:
            Base.metadata.create_all(self.engine)

        logger.debug(f"Created Database class: {self.__dict__}")

        # Enable Foreign Keys support for SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(
            dbapi_connection, connection_record
        ):  # pylint: disable=unused-argument
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @property
    def engine(self):
        """Create SQLAlchemy engine."""

        db_file = Path(self.path, self.name)
        # SQLite 'database is locked' workaround for multiprocessing.
        # In the future, when we'll support others DB drivers,
        # using sqlite should imply settings.processes=1 and disable multiprocessing
        connect_args = {"timeout": 300}
        engine = create_engine(
            f"sqlite+pysqlite:///{db_file}",
            future=True,
            connect_args=connect_args,
        )

        return engine

    def get_active_revision(self):
        """Get the active revision number from database."""

        revision_stmt = select(Revision.id).where(Revision.is_active.is_(True))

        with Session(self.engine) as session:
            try:
                revision_id = session.execute(revision_stmt).one()[0]
            except NoResultFound:
                raise FaddrDatabaseNoRevisionsActive from None
            except MultipleResultsFound:
                raise FaddrDatabaseMultipleRevisionsActive from None
        self.revision_id = revision_id
        logger.debug(f"Active revision_id is {self.revision_id}")
        return self

    def set_active_revision(self):
        """Set current revision as active."""

        stmt_activate_revision = (
            update(Revision)
            .where(Revision.id == self.revision_id)
            .values(is_active=True)
        )
        stmt_deactivate_other_revisions = (
            update(Revision)
            .where(Revision.id != self.revision_id)
            .values(is_active=False)
        )
        with Session(self.engine) as session:
            session.execute(stmt_activate_revision)
            session.execute(stmt_deactivate_other_revisions)
            session.commit()

    def new_revision(self):
        """Create new revision and IP it."""

        revision = Revision()
        with Session(self.engine) as session:
            session.add(revision)
            session.commit()

            self.revision_id = revision.id
        logger.debug(f"Created new revision: '{self.revision_id}'")

        return self

    def cleanup(self):
        """Delete revisions that exceed the maximum number of allowed revisions."""

        logger.debug(f"'database.revision_limit' is '{self.revision_limit}'")
        if self.revision_limit < 0:
            logger.debug(
                f"'database.revision_limit' is '{self.revision_limit}', keeping all revisions."
            )
            return 0

        inactive_revisions = []

        stmt_inactive_revisions = select(Revision.id, Revision.created).where(
            Revision.is_active.is_(False)
        )
        with Session(self.engine) as session:
            for row in session.execute(stmt_inactive_revisions).all():
                inactive_revisions.append(RevisionSchema.from_orm(row))
        logger.debug(f"Found {len(inactive_revisions)} inactive revisions.")

        spare_revision_count = len(inactive_revisions) - self.revision_limit + 1
        if spare_revision_count < 1:
            logger.debug("Nothing to delete.")
            return 0

        inactive_revisions.sort(key=lambda x: x.created)
        revisions_to_delete = [
            revision.id for revision in inactive_revisions[:spare_revision_count]
        ]
        logger.debug(f"Revisions to delete: {len(revisions_to_delete)}")

        stmt_delete_revisions = delete(Revision).where(
            Revision.id.in_(revisions_to_delete)
        )
        with Session(self.engine) as session:
            session.execute(stmt_delete_revisions)
            session.commit()

        return len(revisions_to_delete)

    def insert_device(self, device_data):
        """Insert device data to database."""

        device = make_sa_object(Device, DeviceSchema.parse_obj(device_data))
        device.revision_id = self.revision_id

        with Session(self.engine) as session:
            session.add(device)
            session.commit()

        logger.debug(f"Inserted device: '{device_data['name']}'")

    def find_networks(self, queries):
        """Find provided networks."""

        result = {}

        for query in queries:
            result.update(self.find_network(query))

        return result

    def find_network(self, query):
        """Find provided network."""

        if self.revision_id is None:
            self.get_active_revision()

        logger.debug(f"Using revision_id {self.revision_id}")

        netmask_max = 16
        netmask_min = 32

        logger.debug(f"Searching for {query}")

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
                Device.revision_id == self.revision_id,
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
