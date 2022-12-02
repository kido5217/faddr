"""Package-specific exceptions."""


class FaddrBaseException(Exception):
    """General base exception."""


class FaddrDatabaseDirError(FaddrBaseException):
    """Exception raised whed Database path doesn't exist."""

    def __init__(self, path, problem):
        self.path = path
        self.problem = problem
        self.message = f"{self.path}: {self.problem}"
        super().__init__(self.message)


class FaddrDatabaseMultipleRevisionsActive(FaddrBaseException):
    """Exception raised when more than one revision is active."""


class FaddrDatabaseNoRevisionsActive(FaddrBaseException):
    """Exception raised when more than one revision is active."""


class FaddrDatabaseUnknownQueryType(FaddrBaseException):
    """Exception raised when requested query type isn't supported."""

    def __init__(self, query_type):
        self.query_type = query_type
        self.message = f"Requested query type '{self.query_type}' isn't supported."
        super().__init__(self.message)


class FaddrRancidPathError(FaddrBaseException):
    """Exception raised when requested path doesn't exist."""

    def __init__(self, path):
        self.path = path
        self.message = (
            f"Path {self.path} doesn't exist or isn't valid RANCID directory."
        )
        super().__init__(self.message)


class FaddrRepoPathError(FaddrBaseException):
    """Exception raised when requested path doesn't exist."""

    def __init__(self, path):
        self.path = path
        self.message = f"Path {self.path} doesn't exist of isn't a valid path."
        super().__init__(self.message)


class FaddrRepoUnsupported(FaddrBaseException):
    """Exception raised when repo kind isn't supported."""

    def __init__(self, kind):
        self.kind = kind
        self.message = f"Repo kind {self.kind} isn't supported."
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
