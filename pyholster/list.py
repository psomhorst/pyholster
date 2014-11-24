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

        object.__setattribute__(self, 'address', kwargs.get('address'))
        object.__setattribute__(self, 'name', kwargs.get('name', None))
        object.__setattribute__(self, 'description', kwargs.get('description', None))
        object.__setattribute__(self, 'access_level', kwargs.get('access_level'))

    def __setattribute__(self, *args, **kwargs):
        """Prevent direct setting of attributes."""

        raise errors.MailgunNotSettableError(
            'Attributes of the MailingList cannot be set directly. Use the update() method.')

    def __getattribute__(self, attribute):
        if attribute == 'members' and self.members is None:
            self.load_members

        return object.__getattribute__(self, attribute)

    ##
    # Class methods
    ##

    @classmethod
    def load(cls, address):
        try:
            response = api.get('/lists/{}'.format(address))
        except errors.MailgunRequestException:
            raise LookupError('Could not load MailingList from Mailgun.')
        else:
            data = response.json()

            return cls(address=address,
                       name=data.get('name', None),
                       description=data.get('description', None),
                       access_level=data.get('access_level'))

    ##
    # Getter, setters, deleters
    ##

    def update(self):
        raise NotImplementedError('Not yet implemented')

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
        data = response.json()
        object.__setattribute__(self, 'members',
                                [Member(mailing_list=self, **member) for member in data['items']])
        return self.members

    def add_member(self, member):
        self.members.append(member)

    def add_members(self, members):
        self.members.extend(members)

    def get_members_by_vars(self, *vars_):
        """Returns a generator generating a filtered list of members based on the passed variables
        (plural)."""

        members = [member for member in self.members
                   if all(member.vars[var] == value for var, value in vars_)]
        if len(members):
            for member in members:
                yield member
        else:
            return None

    def get_members_by_var(self, var, value):
        """Returns a generator generating a filtered list of members based on the passed variable
        (singular)."""

        try:
            return self.get_members_by_vars((var, value))
        except StopIteration:
            return None

    def get_member_by_vars(self, *vars_):
        """Returns the first member that is encountered in the list of members filtered by the
        passed variables (plural)."""

        try:
            return next(self.get_members_by_vars(*vars_))
        except StopIteration:
            return None

    def get_member_by_var(self, var, value):
        """Returns the first member that is encountered in the list of members filtered by the
        passed variable (singular)."""

        try:
            return next(self.get_member_by_var(var, value))
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
            self.__class__.load(self.address)
        except errors.MailgunRequestException:
            return False
        else:
            return True
