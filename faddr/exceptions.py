class FaddrBaseException(Exception):
    """General base exception."""

    pass


class FaddrDatabaseNotWritable(FaddrBaseException):
    """Exception raised whed Database can not be opened for writing"""

    pass
