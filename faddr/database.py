"""Database operations."""

from datetime import datetime
from pathlib import Path

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
        self.revision = None

    def new(self, revision=None):
        """Create new revision and return it."""
        if revision:
            self.revision = revision
        else:
            self.revision = self.gen_revision()

        rev_name = Path(self.basename).stem + "-" + self.revision
        suffix = Path(self.basename).suffix
        self.name = rev_name + suffix

        return self.revision

    def insert(self, data):
        """Insert data to database."""

    def get_all(self):
        """Get all data from database or specified table."""

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
