"""Package-specific exceptions."""


class FaddrBaseException(Exception):
    """General base exception."""


class FaddrDatabaseNotWritable(FaddrBaseException):
    """Exception raised whed Database can not be opened for writing."""


class FaddrRancidPathError(FaddrBaseException):
    """Exception raised when requested path doesn't exist."""

    def __init__(self, path):
        self.path = path
        self.message = f"Path {self.path} does not exist or isn't directory."
        super().__init__(self.message)


class FaddrRancidRepoConfigFileFormatError(FaddrBaseException):
    """Exception raised when config file doesn't have correct content-type."""

    def __init__(self, path):
        self.path = path
        self.message = f"File {self.path} does not have correct content-type."
        super().__init__(self.message)


class FaddrSettingsFileFormatError(FaddrBaseException):
    """Exception raised when setting file contains errors and can't be loaded."""

    def __init__(self, path, err):
        self.path = path
        self.err = str(err).replace("\n", ": ")
        self.message = f"File '{self.path}' contains errors: '{self.err}'"
        super().__init__(self.message)


class FaddrParserUnknownProfile(FaddrBaseException):
    """Exception raised when requesting unknonw profile."""

    def __init__(self, profile):
        self.profile = profile
        self.message = f"Profile {self.profile} does not exist."
        super().__init__(self.message)


class FaddrParserConfigFileAbsent(FaddrBaseException):
    """Exception raised when configuration file does not exist."""

    def __init__(self, path):
        self.path = path
        self.message = f"File '{self.path}' does not exist."
        super().__init__(self.message)
