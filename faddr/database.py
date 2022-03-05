"""Database operations."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

from faddr.exceptions import FaddrDatabaseDirError


Base = declarative_base()


class Device(Base):
    """ORM Device data mapping."""

    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    name = Column(String)
    source = Column(String)


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

    def insert_device(self, data):
        """Insert device data to database."""

        with Session(self.engine) as session:
            device = Device(**data["info"])
            session.add(device)
            session.commit()
            print(device.id)

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

    def find_network(self, network):
        """Find provided netwkork."""

    @staticmethod
    def gen_revision():
        """Generate revision."""
        date_format = "%Y%m%d%H%M%S"
        revision = datetime.now().strftime(date_format)

        return revision
