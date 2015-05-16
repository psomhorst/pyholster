"""Send requests to Mailgun and handle responses."""

import requests
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

baseurl = 'https://api.mailgun.net/v3'
apikey = None

class APIKeyError(Exception): pass
class ConnectionError(Exception): pass
class TokenError(Exception): pass

class CommunicationError(Exception): pass
class BadRequest(CommunicationError): pass
class Unauthorized(CommunicationError): pass
class Failed(CommunicationError): pass
class NotFound(CommunicationError): pass
class NotAcceptable(CommunicationError): pass
class ServerError(CommunicationError): pass

html_status_codes = {
    400: BadRequest,
    401: Unauthorized,
    402: Failed,
    404: NotFound,
    406: NotAcceptable,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError
}

def set_key(key):
    """Set the API key to use."""

    global apikey
    apikey = key


def get(url, params={}):
    """Send a GET request."""

    if not apikey:
        raise APIKeyError("No API key provided.")

    url = baseurl + url

    logger.debug("PH GET: {}, {}".format(url, params))

    try:
        response = handle_response(
            requests.get(url, auth=('api', apikey), params=params))

        return response.json()

    except requests.exceptions.ConnectionError as E:
        raise ConnectionError() from E


def post(url, data, files=None):
    """Send a POST request."""

    if not apikey:
        raise APIKeyError("No API key provided.")

    url = (baseurl + url).format(**globals())

    logger.debug("PH GET: {}, {}".format(url, data))

    try:
        attributes = {'auth': ('api', apikey),
                      'data': (data)}

        if files:
            attributes['files'] = files

        response = handle_response(
            requests.post(url, **attributes), (url, attributes))

        return response.json()

    except requests.exceptions.ConnectionError as E:
        raise ConnectionError() from E


def put(url, data):
    """Send a PUT request."""

    if not apikey:
        raise APIKeyError("No API key provided.")

    url = baseurl + url

    logger.debug("PH GET: {}, {}".format(url, data))

    try:
        response = handle_response(
            requests.put(url, auth=('api', apikey), data=data))

        return response.json()

    except requests.exceptions.ConnectionError as E:
        raise ConnectionError() from E


def delete(url):
    """Send a DELETE request."""

    if not apikey:
        raise APIKeyError("No API key provided.")

    url = baseurl + url

    logger.debug("PH GET: {}".format(url))

    try:
        response = handle_response(
            requests.delete(url, auth=('api', apikey)))

        return response.json()

    except requests.exceptions.ConnectionError as E:
        raise ConnectionError() from E


def handle_response(r, *args, **kwargs):
    """Handle the response from Mailgun."""

    message = "[{request[method]}] {request[url]} :: {reason}".format(
        request=r.request.__dict__, reason=r.reason)

    logger.debug("PH handle: {} || {} || {}".format(r, dir(r), r.text))

    try:
        r.json()
    except ValueError as E:
        raise ServerError(
            "[{req[method]}] {req[url]} :: {code} :: {code_type} :: {text} :: {reason}"
            .format(code=r.status_code, code_type=str(type(r.status_code)),
                    req=vars(r.request), text=r.text, reason=r.reason)) from E

    if 'token' in r.json():
        if not _verify_token(r.json()):
            raise TokenError("The Token could not be verified.")

    if r.status_code in html_status_codes:
        raise html_status_codes[r.status_code](message)

    elif r.status_code != 200:
        raise ServerError(
            "[{req[method]}] {req[url]} :: {code} :: {code_type} :: {reason}"
            .format(code=r.status_code, code_type=str(type(r.status_code)),
                    req=r.request.__dict__, reason=r.reason))

    return r


def _verify_token(params):
    """Verify the token sent by Mailgun."""

    return params['signature'] == hmac.new(
        key=globals()['apikey'],
        msg='{}{}'.format(params['timestamp'], params['token']),
        digestmod=hashlib.sha256).hexdigest()

hooks = dict(response=handle_response)

GET = get
PUT = put
POST = post
DELETE = delete
