class MailgunException(Exception):
    pass


class MailgunRequestException(MailgunException):
    pass


class MailgunBadRequest(MailgunRequestException):
    pass


class MailgunUnauthorized(MailgunRequestException):
    pass


class MailgunFailed(MailgunRequestException):
    pass


class MailgunNotFound(MailgunRequestException):
    pass


class MailgunServerError(MailgunRequestException):
    pass


class MailgunUnknown(MailgunRequestException):
    pass


class MailgunNotAcceptable(MailgunRequestException):
    pass


class MailgunNotSettableError(MailgunException):
    pass


class MailgunVerifyFailed(MailgunException):
    pass


class MailgunDuplicateAddress(MailgunException):
    pass

html_status_codes = {
    400: MailgunBadRequest,
    401: MailgunUnauthorized,
    402: MailgunFailed,
    404: MailgunNotFound,
    406: MailgunNotAcceptable,
    500: MailgunServerError,
    502: MailgunServerError,
    503: MailgunServerError,
    504: MailgunServerError
}
