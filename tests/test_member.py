import responses
import json
import yaml
import os
import pytest

import pyholster as ph


def load_fixture(filename):
    path = os.path.join(os.path.dirname(__file__), 'fixtures/', filename)
    with open(path, 'r') as stream:
        if filename.endswith('yml'):
            return yaml.load(stream)
        elif filename.endswith('json'):
            return json.load(stream)
        raise ValueError("Filename should end with '.yml' or '.json'.")


class TestMember:

    def test_init(self):
        member = ph.Member(address='test@testing.test',
                           vars={'age': 100},
                           mailing_list=True)
        assert member.vars['age'] == 100
        assert member.address == 'test@testing.test'

        with pytest.raises(KeyError):
            ph.Member()
        with pytest.raises(KeyError):
            ph.Member(address='test')

    @responses.activate
    def test_load(self):
        fixt_member = load_fixture('members.yml')['items'][0]
        fixt_lst = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}'.format(fixt_lst['address']),
                      body=json.dumps(dict(list=fixt_lst)),
                      status=200)

        mailing_list = ph.MailingList.load(fixt_lst['address'])

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}/members/{}'.format(mailing_list.address,
                                                                     fixt_member['address']),
                      body=json.dumps(dict(member=fixt_member)),
                      status=200)

        member = ph.Member.load(mailing_list, fixt_member['address'])

        for attr in ('name', 'address', 'vars', 'subscribed'):
            assert getattr(member, attr) == fixt_member.get(attr)

    @responses.activate
    def test_update(self):
        member = load_fixture('members.yml')['items'][0]
        fixt_lst = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}'.format(fixt_lst['address']),
                      body=json.dumps(dict(list=fixt_lst)),
                      status=200)

        mailing_list = ph.MailingList.load(fixt_lst['address'])

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}/members/{}'.format(mailing_list.address,
                                                                     member['address']),
                      body=json.dumps(dict(member=member)),
                      status=200)

        def put_callback(request):
            print request.body
            body = json.loads(request.body)
            assert body['address'] == 'newaddress@tests.eu'
            return (200, {}, "{}")

        responses.add_callback(responses.PUT,
                               ph.api.baseurl + '/lists/{}/members/{}'.format(
                                   mailing_list.address, member['address']),
                               callback=put_callback,
                               content_type='application/json')

        member = ph.Member.load(mailing_list, member['address'])
        member.update(address='newaddress@tests.eu', subscribed=False)

        assert member.address == 'newaddress@tests.eu'
        assert not member.subscribed

    @responses.activate
    def test_delete(self):
        fixt_member = load_fixture('members.yml')['items'][0]
        fixt_lst = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}'.format(fixt_lst['address']),
                      body=json.dumps(dict(list=fixt_lst)),
                      status=200)

        mailing_list = ph.MailingList.load(fixt_lst['address'])

        responses.add(responses.GET,
                      ph.api.baseurl + '/lists/{}/members/{}'
                      .format(mailing_list.address,
                              fixt_member['address']),
                      body=json.dumps(dict(member=fixt_member)),
                      status=200)

        responses.add(responses.DELETE,
                      ph.api.baseurl + '/lists/{}/members/{}'
                      .format(mailing_list.address,
                              fixt_member['address']),
                      body="{}",
                      status=200)

        member = ph.Member.load(mailing_list, fixt_member['address'])
        member.delete()

        responses.reset()

        responses.add(responses.DELETE,
                      ph.api.baseurl + '/lists/{}/members/{}'
                      .format(mailing_list.address,
                              fixt_member['address']),
                      body="{}",
                      status=404)

        with pytest.raises(ph.errors.MailgunRequestException):
            member.delete()

    def test_implement(self):
        pass

    def test_is_implemented(self):
        pass
