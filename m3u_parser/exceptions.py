class UrlReadException(Exception):
    """Raised when there is an issue reading content from a URL."""

    pass


class NestedKeyException(Exception):
    """Raised when the nested key format is incorrect or key is not nested."""

    pass


class KeyNotFoundException(Exception):
    """Raised when a specified key is not found in the stream information."""

    pass


class FiltersMissingException(Exception):
    """Raised when an filter word/s is missing."""

    pass


class SavingNotSupportedException(Exception):
    """Raised when saving to a specific format is not supported."""

    pass


class UnrecognizedFormatException(Exception):
    """Raised when a specific format is not supported."""

    pass


class NoContentToParseException(Exception):
    """Raised when the content is not available in the stream."""

    pass


class NoStreamsException(Exception):
    """Raised when streams information is not available."""

    pass
