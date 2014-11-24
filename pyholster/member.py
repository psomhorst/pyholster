import json

from . import request
from . import errors


class Member(object):

    """Describes a MailingList member"""

    address = None
    name = None
    vars = None
    subscribed = None
    mailing_list = None

    ##
    # Magic methods
    # #

    def __init__(self, **kwargs):

        object.__setattr__(self, 'address', kwargs.get('address'))
        object.__setattr__(self, 'name', kwargs.get('name', None))
        object.__setattr__(self, 'vars', kwargs.get('vars', '{}'))
        object.__setattr__(self, 'subscribed', kwargs.get('subscribed', True))
        object.__setattr__(self, 'mailing_list', kwargs.get('mailing_list'))

    def __setattribute__(self, *args, **kwargs):
        """Prevent direct setting of attributes."""

        raise errors.MailgunNotSettableError(
            'Attributes of the Member cannot be set directly. Use the update() method.')

    ##
    # Class methods
    ##

    @classmethod
    def load(cls, list, address):
        try:
            response = request.get('/lists/{}/members/{}'.format(list.address, address))
        except errors.MailgunRequestException:
            raise LookupError(
                'Could not load Members for MailingList {} from Mailgun.'.format(list.address))
        else:
            data = response.json()

            return cls(address=address,
                       name=data.get('name', None),
                       vars=data.get('vars', '{}'),
                       subscribed=data.get('subscribed'))

    ##
    # Getters and setters
    ##

    def update(self, **kwargs):
        """Update the given attributes (by key=value) and send to Mailgun."""

        if not self.is_implemented():
            raise errors.MailgunException(
                'Can not update non-implemented Member. Insert first.')

        if 'mailing_list' in kwargs:
            raise errors.MailgunNotSettableError(
                "The MailingList can not be changed. "
                "Create a new Member instance for another MailingList.")

        update_data = {}

        for key in set(kwargs.keys()) & set(['name', 'description', 'access_level']):
            object.__setattr__(self, key, kwargs.get(key))
            update_data[key] = kwargs.get(key)

        if 'address' in kwargs:
            object.__setattr__(self, 'new_address', kwargs.get('address'))
            update_data['address'] = kwargs.get('address')

        if 'vars' in kwargs:
            object.__setattr__(self, 'vars', kwargs.get('vars'))
            update_data['vars'] = json.dumps(kwargs.get('vars'))

        try:
            request.put('/lists/{}/members/{}'.format(self.mailing_list.address, self.address),
                        update_data)
        except errors.MailgunRequestException:
            raise
        else:
            if hasattr(self, 'new_address'):
                object.__setattr__(self, 'address', self.new_address)
                delattr(self, 'new_address')
            return True

    def delete(self):
        try:
            request.delete('/lists/{}/members/{}'.format(self.mailing_list.address, self.address))
        except errors.MailgunRequestException:
            raise
        else:
            return True

    def implement(self):
        """Implements a member for the first time on Mailgun. Don't use for updates."""

        if self.is_implemented():
            raise errors.MailgunException('This address is already in the MailingList on Mailgun.')

        if hasattr(self, 'new_address'):
            raise errors.MailgunException(
                'The new_address attribute cannot be set for new Members.')

        data = {'address': self.address,
                'name': self.name,
                'vars': json.dumps(self.vars),
                'subscribed': self.subscribed,
                'upsert': False}

        try:
            request.post('/lists/{}/members'.format(self.mailing_list.address), data)
        except errors.MailgunRequestException:
            raise
        else:
            return True

    ##
    # Checkers
    ##

    def is_implemented(self):
        """Checks whether a Member with this address is implemented by trying to load it from
        Mailgun."""

        try:
            self.__class__.load(self.mailing_list, self.address)
        except errors.MailgunRequestException:
            return False
        else:
            return True
