import responses
import types
import pytest
from dateutil import parser as dtparser
import json

from utils import load_fixture

import pyholster as ph


class TestRoute:

    def test_init(self):
        with pytest.raises(KeyError):
            ph.Route()
        with pytest.raises(ValueError):
            ph.Route(actions="stuff")
        with pytest.raises(KeyError):
            ph.Route(expression="string")

        route = ph.Route(priority=5,
                         description="random string",
                         expression="valid expression",
                         actions=["valid action", "valid action"])
        assert route.id is None
        assert route.priority is 5
        assert route.description == "random string"

    def test_setattr(self):
        route = ph.Route(expression="random string", actions=["some string"])
        with pytest.raises(AttributeError):
            route.id = 0
        with pytest.raises(AttributeError):
            route.actions = ["dingen"]

    @responses.activate
    def test_load(self):
        fixt = load_fixture('routes.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body=json.dumps(dict(route=fixt)))

        route = ph.Route.load(format(fixt['id']))
        for attr in ('id', 'description', 'expression', 'actions'):
            assert getattr(route, attr) == fixt[attr]

        assert dtparser.parse(fixt['created_at']) == route.created_at

    @responses.activate
    def test_load_all(self):
        fixtures = load_fixture('routes.yml')['items']
        responses.add(responses.GET,
                      ph.api.baseurl + '/routes',
                      status=200,
                      body=json.dumps(dict(items=fixtures)))

        routes = ph.Route.load_all()
        assert isinstance(routes, types.GeneratorType)

        routes = list(routes)
        assert len(routes) == len(fixtures)

        assert all(isinstance(route, ph.Route) for route in routes)
        assert set(map(lambda x: x.id, routes)) == set(map(lambda x: x['id'], fixtures))

    @responses.activate
    def test_update(self):
        fixt = load_fixture('routes.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body=json.dumps(dict(route=fixt)))

        route = ph.Route.load(format(fixt['id']))

        with pytest.raises(AttributeError):
            route.update(id=6)
        with pytest.raises(ph.errors.MailgunRequestException):
            route.update(priority=1)

        responses.add(responses.PUT,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body="{}")

        route.update(priority=1, description="This is random.")

        assert route.priority is 1
        assert route.description == "This is random."
        assert route.actions == fixt['actions']

        responses.reset()

        with pytest.raises(ph.errors.MailgunException):
            route.update(priority=1)

    @responses.activate
    def test_implement(self):

        responses.reset()

        route = ph.Route(priority=5,
                         description="random string",
                         expression="valid expression",
                         actions=["valid action", "valid action"])

        with pytest.raises(ph.errors.MailgunRequestException):
            route.implement()

        responses.add(responses.POST,
                      ph.api.baseurl + '/routes',
                      status=200,
                      body="{}")

        route.implement()

    @responses.activate
    def delete(self):
        fixt = load_fixture('routes.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body=json.dumps(dict(route=fixt)))

        responses.add(responses.DELETE,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body="{}")

        route = ph.Route.load(format(fixt['id']))

        route.delete()

        responses.reset()

        with pytest.raises(ph.errors.MailgunRequestException):
            route.delete()

    @responses.activate
    def is_implemented(self):
        route = ph.Route(priority=5,
                         description="random string",
                         expression="valid expression",
                         actions=["valid action", "valid action"])

        assert not route.is_implemented()

        fixt = load_fixture('routes.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/routes/{}'.format(fixt['id']),
                      status=200,
                      body=json.dumps(dict(route=fixt)))

        route = ph.Route.load(format(fixt['id']))

        assert route.is_implemented()

        responses.reset()

        assert not route.is_implemented()
