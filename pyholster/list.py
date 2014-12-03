import json

from . import errors
from . import api
from .member import Member


class MailingList(object):

    address = None
    name = None
    description = None
    access_level = None
    members = None

    ##
    # Magic methods
    ##

    def __init__(self, **kwargs):

        object.__setattr__(self, 'address', kwargs.get('address'))
        object.__setattr__(self, 'name', kwargs.get('name', None))
        object.__setattr__(self, 'description', kwargs.get('description', None))
        object.__setattr__(self, 'access_level', kwargs.get('access_level'))

    def __setattr__(self, *args, **kwargs):
        """Prevent direct setting of attributes."""

        raise errors.MailgunNotSettableError(
            'Attributes of the MailingList cannot be set directly. Use the update() method.')

    def __getattribute__(self, attribute):
        if attribute == 'members' and object.__getattribute__(self, 'members') is None:
            self.load_members()

        return object.__getattribute__(self, attribute)

    ##
    # Class methods
    ##

    @classmethod
    def load(cls, address):
        try:
            response = api.get('/lists/{}'.format(address))
        except errors.MailgunException:
            raise LookupError('Could not load MailingList from Mailgun.')
        else:
            data = response['list']
            return cls(address=address,
                       name=data.get('name', None),
                       description=data.get('description', None),
                       access_level=data.get('access_level'))

    @classmethod
    def load_all(cls):
        try:
            response = api.get('/lists')
        except errors.MailgunRequestException:
            raise LookupError('Could not load any MailingLists from Mailgun.')
        else:
            return (cls(**m) for m in response['items'])

    ##
    # Getter, setters, deleters
    ##

    def update(self, **kwargs):
        """Update the given attributes (by key=value) and send to Mailgun."""

        if not self.is_implemented():
            raise errors.MailgunException(
                'Can not update non-implemented Member. Insert first.')

        update_data = {}

        for key in set(kwargs.keys()) & set(['name', 'description', 'access_level']):
            object.__setattr__(self, key, kwargs.get(key))
            update_data[key] = kwargs.get(key)

        if 'address' in kwargs:
            object.__setattr__(self, 'new_address', kwargs.get('address'))
            update_data['address'] = kwargs.get('address')

        try:
            api.put('/lists/{}'.format(self.address),
                    update_data)
        except errors.MailgunRequestException:
            raise
        else:
            if hasattr(self, 'new_address'):
                object.__setattr__(self, 'address', self.new_address)
                delattr(self, 'new_address')
            return True

    def implement(self):
        """Implements a MailingList for the first time on Mailgun. Don't use for updates."""

        if self.is_implemented():
            raise errors.MailgunException('This MailingList is already implemented on Mailgun.')

        if hasattr(self, 'new_address'):
            raise errors.MailgunException(
                'The new_address attribute cannot be set for a new MailingList.')

        data = {'address': self.address,
                'name': self.name,
                'description': self.description,
                'access_level': self.access_level}

        try:
            api.post('/lists', data)
        except errors.MailgunRequestException:
            raise
        else:
            return True

    def delete(self):
        try:
            api.delete('/lists/{}'.format(self.address))
        except errors.MailgunRequestException:
            raise
        else:
            return True

    ##
    #  Members: getting, setting, removing
    ##

    def load_members(self):
        response = api.get('/lists/{}/members'.format(self.address))
        object.__setattr__(self, 'members',
                           [Member(mailing_list=self, **member) for member in response['items']])
        return self.members

    def add_members_dictlist(self, members):
        object.__setattr__(self, 'members', None)
        api.post('/lists/{}/members.json'.format(self.address),
                 dict(upsert=True, members=json.dumps(members)))

    def get_members_by_vars(self, **vars_):
        """Returns a generator generating a filtered list of members based on the passed variables
        (plural)."""
        print [m.vars for m in self.members]
        members = [member for member in self.members
                   if all(member.vars[var] == value for var, value in vars_.iteritems())]
        if len(members):
            for member in members:
                yield member

    def get_members_by_var(self, var, value):
        """Returns a generator generating a filtered list of members based on the passed variable
        (singular)."""

        try:
            return self.get_members_by_vars(**{var: value})
        except StopIteration:
            return None

    def get_member_by_vars(self, **vars_):
        """Returns the first member that is encountered in the list of members filtered by the
        passed variables (plural)."""

        try:
            return next(self.get_members_by_vars(**vars_))
        except StopIteration:
            return None

    def get_member_by_var(self, var, value):
        """Returns the first member that is encountered in the list of members filtered by the
        passed variable (singular)."""

        try:
            return next(self.get_members_by_var(var, value))
        except StopIteration:
            return None

    def get_member_by_address(self, address):
        """Gets a member based on his address."""
        try:
            return next(member for member in self.members if member.address == address)
        except StopIteration:
            return None

    def delete_all_members(self):
        def internal():
            for member in self.members():
                try:
                    member.delete()
                    yield True
                except errors.MailgunRequestException:
                    raise
        return all(internal())

    def is_implemented(self):
        """Checks whether a MailingList with this address is implemented by trying to load it from
        Mailgun."""

        try:
            print self.__class__.load(self.address)
        except LookupError:
            return False
        else:
            return True
