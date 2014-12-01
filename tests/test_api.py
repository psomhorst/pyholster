import pyholster as ph
import responses
import json
import pytest

from utils import load_fixture


class TestAPI:

    class TestRoutes:

        @responses.activate
        def test_get(self):

            responses.add(responses.GET,
                          ph.api.baseurl + '/testing/',
                          status=200,
                          body=json.dumps(load_fixture('random.json')))
            respons = ph.api.get('/testing/')
            assert respons == load_fixture('random.json')

        @responses.activate
        def test_post(self):
            responses.add(responses.POST,
                          ph.api.baseurl + '/testing/',
                          status=200,
                          body=json.dumps({'message': "OK"}))
            respons = ph.api.post('/testing/', {'data': load_fixture('random.json')})
            assert respons == dict(message="OK")

        @responses.activate
        def test_put(self):
            responses.add(responses.PUT,
                          ph.api.baseurl + '/testing/',
                          status=200,
                          body=json.dumps({'message': "OK"}))
            respons = ph.api.put('/testing/', {'data': load_fixture('random.json')})
            assert respons == dict(message="OK")

        @responses.activate
        def test_delete(self):
            responses.add(responses.DELETE,
                          ph.api.baseurl + '/testing/',
                          status=200,
                          body=json.dumps({'message': "OK"}))
            respons = ph.api.delete('/testing/')
            assert respons == dict(message="OK")

    class TestHooks:

        @responses.activate
        def test_200(self):
            responses.add(responses.GET,
                          ph.api.baseurl + '/status_200',
                          status=200,
                          body=json.dumps(dict(message="OK")))
            respons = ph.api.get('/status_200')
            assert respons == dict(message="OK")

        @responses.activate
        def test_400(self):
            for action in ('GET', 'POST', 'DELETE', 'PUT'):

                responses.add(getattr(responses, action),
                              ph.api.baseurl + '/status_400',
                              status=400,
                              body=json.dumps(dict(message="OK")))

                with pytest.raises(ph.errors.MailgunBadRequest):
                    func = getattr(ph.api, action)
                    if action in ("POST", "PUT"):
                        func('/status_400', dict(input='random'))
                    else:
                        func('/status_400')
