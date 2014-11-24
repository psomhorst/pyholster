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
