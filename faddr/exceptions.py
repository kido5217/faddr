"""Packege-specific exceptions."""


class FaddrBaseException(Exception):

    """General base exception."""


class FaddrDatabaseNotWritable(FaddrBaseException):

    """Exception raised whed Database can not be opened for writing."""


class FaddrDeviceUnsupportedType(FaddrBaseException):

    """Exception raised when Device fabric function gets unsupported device_type."""
