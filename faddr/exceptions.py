"""Package-specific exceptions."""


class FaddrBaseException(Exception):
    """General base exception."""


class FaddrDatabaseNotWritable(FaddrBaseException):
    """Exception raised whed Database can not be opened for writing."""


class FaddrDeviceUnsupportedType(FaddrBaseException):
    """Exception raised when Device fabric function gets unsupported device_type."""


class FaddrRancidRepoUnsupportedLevel(FaddrBaseException):
    """Exception raised when creating RancidRepo with unsupported level."""


class FaddrRancidRepoPathError(FaddrBaseException):
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


class FaddrRancidRepoRouterDBAbsent(FaddrBaseException):
    """Exception raised when router.db isn't present in group dir."""

    def __init__(self, path):
        self.path = path
        self.message = f"Can't find 'router.db' file in {self.path}."
        super().__init__(self.message)
