class PHException(Exception):

    """General exception, parent to all other exceptions."""
    pass


class PHNotSettableError(PHException):
    pass


class PHVerifyFailed(PHException):
    pass


class PHDuplicateAddress(PHException):
    pass


class PHRequestException(PHException):
    """Request exceptions are thrown due to HTTP response codes and descendants
    of PHRequestException."""

    pass


class PHBadRequest(PHRequestException):
    """Server returned a 400 `Bad Request` code."""

    pass


class PHUnauthorized(PHRequestException):
    """Server returned a 401 `Unauthorized` code."""

    pass


class PHFailed(PHRequestException):
    """Server returned a 402 `Failed` code."""

    pass


class PHNotFound(PHRequestException):
    """Server returned a 404 `Not Found` code."""

    pass


class PHServerError(PHRequestException):
    """Server returned a 500, 502, 503, or 504 `Server Error` code."""

    pass


class PHUnknown(PHRequestException):
    """Server returned a unknown HTTP status code."""

    pass


class PHNotAcceptable(PHRequestException):
    """Server returned a 406 `Not Acceptable` code."""

    pass


html_status_codes = {
    400: PHBadRequest,
    401: PHUnauthorized,
    402: PHFailed,
    404: PHNotFound,
    406: PHNotAcceptable,
    500: PHServerError,
    502: PHServerError,
    503: PHServerError,
    504: PHServerError
}
