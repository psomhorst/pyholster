import json

from . import api


class Member(object):

    """Describes a MailingList member"""

    class MemberNotLoadable(Exception): pass
    class MemberNotImplemented(Exception): pass
    class MemberNotDeleted(Exception): pass
    class MemberNotUpdated(Exception): pass

    ##
    # Magic methods
    # #

    def __init__(self, **kwargs):

        object.__setattr__(self, 'address', kwargs['address'])
        object.__setattr__(self, 'name', kwargs.get('name'))
        object.__setattr__(self, 'vars', kwargs.get('vars', {}))
        object.__setattr__(self, 'subscribed', kwargs.get('subscribed', True))
        object.__setattr__(self, 'mailing_list', kwargs.get('mailing_list'))


    ##
    # Class methods
    ##

    @classmethod
    def load(cls, lst, address):
        try:
            response = api.get('/lists/{}/members/{}'
                               .format(lst.address, address))
        except api.CommunicationError:
            raise cls.MemberNotLoadable(
                "Could not load Member from Mailgun.")

        data = response['member']
        return cls(mailing_list=lst,
                   address=data['address'],
                   name=data.get('name'),
                   vars=data.get('vars', {}),
                   subscribed=data['subscribed'])

    ##
    # Getters and setters
    ##

    def update(self, **kwargs):
        """Update the given attributes (by key=value) and send to Mailgun."""

        if not self.is_implemented():
            raise self.MemberNotImplemented(
                "Can not update non-implemented Member. Insert first.")

        if 'mailing_list' in kwargs:
            raise AttributeError(
                "The MailingList can not be changed. "
                "Create a new Member instance for another MailingList.")

        update_data = {}

        for key in set(kwargs.keys()) & set(['name', 'vars', 'subscribed']):
            object.__setattr__(self, key, kwargs[key])
            update_data[key] = kwargs[key]

        if 'address' in kwargs:
            object.__setattr__(self, 'new_address', kwargs['address'])
            update_data['address'] = kwargs['address']

        if 'vars' in kwargs:
            object.__setattr__(self, 'vars', kwargs['vars'])
            update_data['vars'] = json.dumps(kwargs['vars'])

        try:
            api.put('/lists/{}/members/{}'.format(self.mailing_list.address,
                                                  self.address),
                    update_data)
        except api.CommunicationError as E:
            raise self.MemberNotUpdated("Could not update Member.") from E
        else:
            if hasattr(self, 'new_address'):
                object.__setattr__(self, 'address', self.new_address)
                delattr(self, 'new_address')
            return True

    def delete(self):
        """Delete the Member from Mailgun and, if it succeeds, from the
        MailingList it belongs to."""

        try:
            api.delete(
                '/lists/{}/members/{}'.format(self.mailing_list.address,
                                              self.address))
        except api.CommunicationError as E:
            raise self.MemberNotDeleted("Could not delete Member.") from E
        else:
            try:
                self.mailing_list.members.remove(self)
            except:
                pass
            return True

    def implement(self):
        """Implements a member for the first time on Mailgun. Don't use for
        updates."""

        if self.is_implemented():
            self.update()
            return

        data = {'address': self.address,
                'name': self.name,
                'vars': json.dumps(self.vars),
                'subscribed': self.subscribed,
                'upsert': False}

        try:
            api.post(
                '/lists/{}/members'.format(self.mailing_list.address), data)
        except api.CommunicationError as E:
            raise self.MemberNotImplemented(
                "Could not implement Member.") from E
        else:
            return True

    ##
    # Checkers
    ##

    def upsert(self):
        return self.update() if self.is_implemented() else self.implement()

    def is_implemented(self):
        """Checks whether a Member with this address is implemented by trying
        to load it from Mailgun."""

        try:
            self.__class__.load(self.mailing_list, self.address)
        except self.MemberNotLoadable:
            return False
        else:
            return True
