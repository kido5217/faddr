"""Package-specific exceptions."""


class FaddrBaseException(Exception):
    """General base exception."""


class FaddrDatabaseDirError(FaddrBaseException):
    """Exception raised whed Database path doesn't exist."""

    def __init__(self, path, problem):
        self.path = path
        self.problem = problem
        self.message = f"Wrong {self.path}: {self.problem}"
        super().__init__(self.message)


class FaddrRancidPathError(FaddrBaseException):
    """Exception raised when requested path doesn't exist."""

    def __init__(self, path):
        self.path = path
        self.message = (
            f"Path {self.path} doesn't exist or isn't valid RANCID directory."
        )
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


class FaddrParserConfigFileEmpty(FaddrBaseException):
    """Exception raised when configuration file is empty."""

    def __init__(self, path):
        self.path = path
        self.message = f"File '{self.path}' is empty."
        super().__init__(self.message)
