"""For handling the logging setup and output from the FFI library
As per: https://docs.rs/pact_ffi/0.0.2/pact_ffi/log/index.html
"""

from enum import unique, Enum


@unique
class LogToBufferStatus(Enum):
    """Return codes from a request to setup a logger.

    As per: https://docs.rs/pact_ffi/0.0.2/pact_ffi/log/fn.pactffi_logger_attach_sink.html#error-handling
    """

    SUCCESS = 0  # Operation succeeded
    CANT_SET_LOGGER = -1  # Can't set the logger
    NO_LOGGER = -2  # No logger has been initialized
    SPECIFIER_NOT_UTF8 = -3  # The sink specifier was not UTF-8 encoded
    UNKNOWN_SINK_TYPE = -4  # The sink type specified is not a known type
    MISSING_FILE_PATH = -5  # No file path was specified in the sink specification
    CANT_OPEN_SINK_TO_FILE = -6  # Opening a sink to the given file failed
    CANT_CONSTRUCT_SINK = -7  # Can't construct sink


@unique
class LogLevel(Enum):
    OFF = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5
