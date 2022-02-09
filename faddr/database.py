"""Database operations."""

from datetime import datetime
from pathlib import Path

from tinydb import TinyDB, Query

from faddr.exceptions import FaddrDatabaseDirError


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
        self.timestamp = None

    def new(self, timestamp=None):
        """Create new revision and return timestamp."""
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = self.gen_timestamp()

        rev_name = Path(self.basename).stem + "-" + self.timestamp
        suffix = Path(self.basename).suffix
        self.name = rev_name + suffix

        return self.timestamp

    def insert(self, data):
        """Insert data to database."""
        with TinyDB(Path(self.path, self.name)) as session:
            session.insert(data)

    def get_all(self, table=None):
        """Get all data from database or specified table."""
        with TinyDB(Path(self.path, self.name)) as session:
            if table:
                return session.table(table).all()

            data = {}
            for table_name in session.tables():
                data[table_name] = session.table(table_name).all()
            return data

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
        with TinyDB(Path(self.path, self.name)) as session:
            results = session.search(
                Query().interfaces.any(Query().ipv4.any(Query().network == network))
            )
            return results

    @staticmethod
    def gen_timestamp():
        """Generate timestamp."""
        date_format = "%Y%m%d%H%M%S"
        timestamp = datetime.now().strftime(date_format)

        return timestamp
