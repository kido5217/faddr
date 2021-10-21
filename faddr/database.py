from tinydb import TinyDB


# TODO: redo this, maybe use SQL
class Database:
    def __init__(self, db_file):
        """Create database file, erase previous one if exists."""
        self.db = TinyDB(db_file)
        # TODO: implement db files rotation, for now just replace all data
        self.db.truncate()
        # self.db_path = pathlib.Path(db_file)
        # self.db_file_name = self.db_path.name
        # self.db_dir = self.db_path.parent

    def __db_path_is_writable(self, db_file):
        pass

    def insert(self, data):
        self.db.insert(data)
