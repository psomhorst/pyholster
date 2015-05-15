"""Send requests to Mailgun and handle responses."""

import requests
import hashlib
import hmac

from . import errors

baseurl = 'https://api.mailgun.net/v3'
apikey = None


def set_key(key):
    """Set the API key to use."""

    global apikey
    apikey = key


def get(url, params={}):
    """Send a GET request."""

    if not apikey:
        raise errors.PHException("No API key provided.")

    url = baseurl + url

    try:
        response = handle_response(
            requests.get(url, auth=('api', apikey), params=params))

        return response.json()

    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def post(url, data, files=None):
    """Send a POST request."""

    if not apikey:
        raise errors.MailgunUnauthorized("No API key provided.")

    url = (baseurl + url).format(**globals())

    try:
        attributes = {'auth': ('api', apikey),
                      'data': (data)}

        if files:
            attributes['files'] = files

        response = handle_response(
            requests.post(url, **attributes), (url, attributes))

        return response.json()

    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def put(url, data):
    """Send a PUT request."""

    if not apikey:
        raise errors.MailgunUnauthorized("No API key provided.")

    url = baseurl + url

    try:
        response = handle_response(
            requests.put(url, auth=('api', apikey), data=data))

        return response.json()

    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def delete(url):
    """Send a DELETE request."""

    if not apikey:
        raise errors.MailgunUnauthorized("No API key provided.")

    url = baseurl + url

    try:
        response = handle_response(
            requests.delete(url, auth=('api', apikey)))

        return response.json()

    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def handle_response(r, *args, **kwargs):
    """Handle the response from Mailgun."""

    message = "[{request[method]}] {request[url]} :: {reason}".format(
        request=r.request.__dict__, reason=r.reason)

    if 'token' in r.json():
        if not __verify_token(r.json()):
            raise errors.MailgunVerifyFailed()

    if r.status_code in errors.html_status_codes:
        raise errors.html_status_codes[r.status_code](message)

    elif r.status_code != 200:
        raise errors.MailgunUnknown(
            "[{req[method]}] {req[url]} :: {code} :: {code_type} :: {reason}"
            .format(code=r.status_code, code_type=str(type(r.status_code)),
                    req=r.request.__dict__, reason=r.reason))

    return r


def __verify_token(params):
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
