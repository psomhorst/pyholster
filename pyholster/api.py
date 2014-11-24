import requests
import hashlib
import hmac

from . import errors


baseurl = 'https://api.mailgun.net/v2/'
apikey = None


def set_apikey(apikey_):
    global apikey
    apikey = apikey_


def get(url, params=None):
    if not params:
        params = {}
    url = baseurl + url
    return requests.get(url,
                        auth=('api', apikey),
                        params=params,
                        hooks=hooks).json()


def post(url, data):

    url = (baseurl + url).format(**globals())
    print("[POST] {url} :: {data}"
          .format(url=url,
                  data=','.join('{}={}'.format(k, str(v)) for k, v in data.iteritems())))

    return requests.post(url,
                         auth=('api', apikey),
                         data=data,
                         hooks=hooks).json()


def put(url, data):
    url = baseurl + url
    print("[PUT] {url} :: {data}"
          .format(url=url,
                  data=','.join('{}={}'.format(k, str(v)) for k, v in data.iteritems())))

    return requests.put(url,
                        auth=('api', apikey),
                        data=data,
                        hooks=hooks).json()


def delete(url):
    url = baseurl + url
    print("[DEL] {url}".format(url=url))
    return requests.delete(url, auth=('api', apikey), hooks=hooks).json()


def handle_response(r, *args, **kwargs):
    message = "[{request[method]}] {request[url]} :: {reason}".format(
        request=r.request.__dict__, reason=r.reason)

    if 'token' in r.json():
        if not verify(r.json()):
            raise errors.MailgunVerifyFailed()

    if r.status_code == 400:
        raise errors.MailgunBadRequest(message)

    elif r.status_code == 401:
        raise errors.MailgunUnauthorized(message)

    elif r.status_code == 402:
        raise errors.MailgunFailed(message)

    elif r.status_code == 404:
        raise errors.MailgunNotFound(message)

    elif r.status_code == 406:
        raise errors.MailgunNotAcceptable(message)

    elif r.status_code in (500, 502, 503, 504):
        raise errors.MailgunServerError(message)

    elif r.status_code != 200:
        raise errors.MailgunUnknown(
            "[{request[method]}] {request[url]} :: {code} :: {codetype} :: {reason}"
            .format(code=r.status_code, codetype=str(type(r.status_code)),
                    request=r.request.__dict__, reason=r.reason))


def verify(params):
    return params['signature'] == hmac.new(
        key=globals()['apikey'],
        msg='{}{}'.format(params['timestamp'], params['token']),
        digestmod=hashlib.sha256).hexdigest()

hooks = dict(response=handle_response)
