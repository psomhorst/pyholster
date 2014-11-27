import requests
import hashlib
import hmac
import json

from . import errors


baseurl = 'https://api.mailgun.net/v2'
apikey = None


def set_apikey(apikey_):
    global apikey
    apikey = apikey_


def get(url, params=None):
    if not params:
        params = {}
    url = baseurl + url
    try:
        return handle_response(requests.get(url,
                                            auth=('api', apikey),
                                            params=params)).json()
    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def post(url, data):

    url = (baseurl + url).format(**globals())
    print("[POST] {url} :: {data}"
          .format(url=url,
                  data=','.join('{}={}'.format(k, str(v)) for k, v in data.iteritems())))
    try:

        return handle_response(requests.post(url,
                                             auth=('api', apikey),
                                             data=json.dumps(data))).json()
    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def put(url, data):
    url = baseurl + url
    print("[PUT] {url} :: {data}"
          .format(url=url,
                  data=','.join('{}={}'.format(k, str(v)) for k, v in data.iteritems())))
    try:
        return handle_response(requests.put(url,
                                            auth=('api', apikey),
                                            data=json.dumps(data))).json()
    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def delete(url):
    url = baseurl + url
    print("[DEL] {url}".format(url=url))
    try:
        return handle_response(requests.delete(url, auth=('api', apikey))).json()

    except requests.exceptions.ConnectionError:
        raise errors.MailgunRequestException


def handle_response(r, *args, **kwargs):
    message = "[{request[method]}] {request[url]} :: {reason}".format(
        request=r.request.__dict__, reason=r.reason)

    print r

    if 'token' in r.json():
        if not verify(r.json()):
            raise errors.MailgunVerifyFailed()

    if r.status_code in errors.html_status_codes:
        raise errors.html_status_codes[r.status_code](message)

    elif r.status_code != 200:
        raise errors.MailgunUnknown(
            "[{request[method]}] {request[url]} :: {code} :: {codetype} :: {reason}"
            .format(code=r.status_code, codetype=str(type(r.status_code)),
                    request=r.request.__dict__, reason=r.reason))

    return r


def verify(params):
    return params['signature'] == hmac.new(
        key=globals()['apikey'],
        msg='{}{}'.format(params['timestamp'], params['token']),
        digestmod=hashlib.sha256).hexdigest()

hooks = dict(response=handle_response)

GET = get
PUT = put
POST = post
DELETE = delete
