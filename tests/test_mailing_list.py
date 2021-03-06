import responses
import json
import types
# import pytest
import os
import copy

import pyholster


from utils import load_fixture


class TestMailingListDry:

    @responses.activate
    def test_load_all(self):
        responses.add(responses.GET, pyholster.api.baseurl + '/lists',
                      body=json.dumps(load_fixture('lists.yml')), status=200,
                      content_type='application/json')

        all_lists = list(pyholster.MailingList.load_all())

        assert len(all_lists) is 2
        assert all(isinstance(l, pyholster.MailingList) for l in all_lists)

    @responses.activate
    def test_load_one(self):
        lists = load_fixture('lists.yml')['items']
        fixt = lists[0]
        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        lst = pyholster.MailingList.load(fixt['address'])

        assert isinstance(lst, pyholster.MailingList)
        assert lst.address == fixt['address']
        assert lst.name == fixt['name']
        assert lst.description == fixt['description']

    @responses.activate
    def test_delete(self):
        fixt = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        responses.add(responses.DELETE,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps(dict(message='OK')))

        lst = pyholster.MailingList.load(fixt['address'])

        assert lst.delete()

    @responses.activate
    def test_update(self):
        fixt = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        responses.add(responses.PUT,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        lst = pyholster.MailingList.load(fixt['address'])

        assert lst.name == fixt['name']

        assert lst.update(name='new name')

        assert lst.name == 'new name'

    @responses.activate
    def test_update_address(self):

        fixt = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        responses.add(responses.PUT,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200, body="{}")

        lst = pyholster.MailingList.load(fixt['address'])

        assert lst.address == fixt['address']

        assert lst.update(address='new@address.uk')

        assert lst.address == 'new@address.uk'

    @responses.activate
    def test_get_members(self):
        fixt = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        fixt_messages = load_fixture('members.yml')

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}/members'.format(fixt['address']),
                      status=200,
                      body=json.dumps(fixt_messages))

        lst = pyholster.MailingList.load(fixt['address'])

        assert object.__getattribute__(lst, 'members') is None
        assert isinstance(lst.members, list)
        print lst.members

        assert all(isinstance(m, pyholster.Member) for m in lst.members)
        assert len(lst.members) is 2

    @responses.activate
    def test_add_member(self):
        fixt = load_fixture('lists.yml')['items'][0]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        fixt_messages = load_fixture('members.yml')

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}/members'.format(fixt['address']),
                      status=200,
                      body=json.dumps(fixt_messages))

        lst = pyholster.MailingList.load(fixt['address'])

        assert object.__getattribute__(lst, 'members') is None
        assert len(lst.members) is 2

        lst.add_member(pyholster.Member(address='baz@lightyear.nl',
                                        name='Baz lightyear',
                                        mailing_list=lst))
        assert len(lst.members) is 3

    @responses.activate
    def test_get_members_by_vars(self):

        fixt = load_fixture('lists.yml')['items'][0]
        fixt_messages = load_fixture('members.yml')

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}/members'.format(fixt['address']),
                      status=200,
                      body=json.dumps(fixt_messages))

        lst = pyholster.MailingList.load(fixt['address'])

        filtered = lst.get_members_by_vars(age=21)
        assert isinstance(filtered, types.GeneratorType)
        assert len(list(filtered)) is 2

        filtered = lst.get_members_by_vars(id=218)
        assert isinstance(filtered, types.GeneratorType)
        assert len(list(filtered)) is 1

        filtered = lst.get_members_by_var('id', 218)
        assert isinstance(filtered, types.GeneratorType)
        assert len(list(filtered)) is 1

        filtered = lst.get_member_by_var('id', 218)
        assert isinstance(filtered, pyholster.Member)

    @responses.activate
    def test_is_implemented(self):
        lists = load_fixture('lists.yml')['items']
        fixt = lists[1]

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=400,
                      body=json.dumps({'list': fixt}))

        lst = pyholster.MailingList(**fixt)

        assert not lst.is_implemented()
        assert len(responses.calls) is 1

        responses.reset()

        responses.add(responses.GET,
                      pyholster.api.baseurl +
                      '/lists/{}'.format(fixt['address']),
                      status=200,
                      body=json.dumps({'list': fixt}))

        lst = pyholster.MailingList.load(fixt['address'])

        assert isinstance(lst, pyholster.MailingList)
        assert lst.address == fixt['address']
        assert lst.name == fixt['name']
        assert lst.description == fixt['description']

class TestMailingListWet:
    def set_apikey(self):
        keypath = os.path.abspath(os.path.dirname(
            os.path.realpath(__file__)) + '/../api.key')

        with open(keypath, 'r') as keyfile:
            pyholster.api.set_apikey(keyfile.read())

    def test_implement_and_destroy(self):
        self.set_apikey()

        create_lists = load_fixture('lists_wet.yml')

        for clist in create_lists['items']:
            try:
                pyholster.MailingList.load(clist['address']).delete()
            except LookupError:
                pass
            mlist = pyholster.MailingList(**clist)
            mlist.implement()

            pyholster.MailingList.load(clist['address'])

            mlist.delete()

    def test_member_management(self):

        self.set_apikey()

        create_lists = load_fixture('lists_wet.yml')['items']
        members = load_fixture('members.yml')['items']
        clist = create_lists[0]

        try:
            pyholster.MailingList.load(clist['address']).delete()
        except LookupError:
            pass
        mlist = pyholster.MailingList(**clist)
        mlist.implement()

        members_adding = copy.copy(members)
        member = members_adding.pop(0)

        mlist.add_member(pyholster.Member(**member))

        mlist.add_members([pyholster.Member(**member)
                           for member in members_adding])

        tlist = pyholster.MailingList.load(clist['address'])
        assert len(tlist.members) == len(members)

        tlist.members[0].delete()

        assert len(tlist.members) == len(members) - 1
