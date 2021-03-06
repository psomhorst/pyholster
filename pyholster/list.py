from . import api
from .member import Member


class MailingList(object):

    """Represent a MailingList in Mailgun. This class manages the alias
    (address), name, description and access level, as well as the members."""

    class MailingListNotLoadable(Exception): pass

    address = None
    name = None
    description = None
    access_level = None
    members = None

    ##
    # Magic methods
    ##

    def __init__(self, **kwargs):
        """Initialize based on existing data."""

        object.__setattr__(self, 'address', kwargs.get('address'))
        object.__setattr__(self, 'name', kwargs.get('name', None))
        object.__setattr__(
            self, 'description', kwargs.get('description', None))
        object.__setattr__(self, 'access_level', kwargs.get('access_level'))

    @property
    def members(self):
        if not hasattr(self, '_members'):
            self._load_members()
        return self._members


    ##
    # Class methods
    ##


    @classmethod
    def load(cls, address):
        """Load a single MailingList by address."""

        try:
            response = api.get('/lists/{}'.format(address))
        except api.CommunicationError:
            raise cls.MailingListNotLoadable(
                "Could not load MailingList from Mailgun.")
        data = response['list']
        return cls(address=address,
                   name=data.get('name', None),
                   description=data.get('description', None),
                   access_level=data.get('access_level'))

    @classmethod
    def load_all(cls):
        """Load all MailingLists."""

        try:
            response = api.get('/lists')
        except api.CommunicationError as E:
            raise LookupError(
                'Could not load any MailingLists from Mailgun.') from E
        else:
            return (cls(**m) for m in response['items'])

    ##
    # Getter, setters, deleters
    ##

    def update(self, safe=True, **kwargs):
        """Update the given attributes (by key=value). Update the MailingList
        at Mailgun if `safe` is True."""

        if safe and not self.is_implemented():
            self.implement()

        update_data = {}

        for key in (set(kwargs.keys())
                    & set(['name', 'description', 'access_level'])):
            if getattr(self, key) != kwargs.get(key):
                object.__setattr__(self, key, kwargs.get(key))
                update_data[key] = kwargs.get(key)

        if 'address' in kwargs and kwargs['address'] != self.address:
            object.__setattr__(self, 'new_address', kwargs.get('address'))
            update_data['address'] = kwargs.get('address')

        if not len(update_data) or not safe:
            return True

        return self._safe(update_data)

    def _safe(self, data):
        """Safe update data to Mailgun."""

        try:
            api.put('/lists/{}'.format(self.address),
                    data)
        except api.CommunicationError as E:
            raise E
        else:
            if hasattr(self, 'new_address'):
                object.__setattr__(self, 'address', self.new_address)
                delattr(self, 'new_address')
            return True

    def implement(self):
        """Implement a MailingList for the first time on Mailgun. Not for
        updating."""

        if self.is_implemented():
            self.update()

        data = {'address': self.address,
                'name': self.name,
                'description': self.description,
                'access_level': self.access_level}

        try:
            api.post('/lists', data)
        except api.CommunicationError:
            raise
        else:
            return self.save_members()

    def delete(self):
        try:
            api.delete('/lists/{}'.format(self.address))
        except api.CommunicationError:
            raise
        else:
            return True

    ##
    #  Members: getting, setting, removing
    ##

    def save_members(self):
        """Insert/safe all set members individually."""

        return all(member.upsert() for member in self.members)

    def _load_members(self):
        """Load all members of the MailingList."""

        response = api.get('/lists/{}/members'.format(self.address))
        self._members = [Member(mailing_list=self, **member)
                         for member in response['items']]


    def add_member(self, member):
        """Add a member to the MailingList."""

        member.mailing_list = self
        member.upsert()
        self.members.append(member)

    def add_members(self, members):
        """Add multiple members to the MailingList."""

        for member in members:
            if isinstance(member, dict):
                member = Member(**member)
            member.mailing_list = self
            member.upsert()

        self.members.extend(members)

    def get_members_by_vars(self, **vars_):
        """Return a generator generating a filtered list of members based on
        the passed variables (plural)."""

        members = [member for member in self.members
                   if all(var in member.vars and member.vars[var] == value
                          for var, value in vars_.items())]

        if len(members):
            for member in members:
                yield member

    def get_members_by_var(self, var, value):
        """Return a generator generating a filtered list of members based on
        the passed variable (singular)."""

        try:
            return self.get_members_by_vars(**{var: value})
        except StopIteration:
            return []

    def get_member_by_vars(self, **vars_):
        """Return the first member that is encountered in the list of members
        filtered by the passed variables (plural)."""

        try:
            return next(self.get_members_by_vars(**vars_))
        except StopIteration:
            return []

    def get_member_by_var(self, var, value):
        """Return the first member that is encountered in the list of members
        filtered by the passed variable (singular)."""

        try:
            return next(self.get_members_by_var(var, value))
        except StopIteration:
            return []

    def get_member_by_address(self, address):
        """Get a member based on his address."""
        try:
            return next(member for member in self.members
                        if member.address == address)
        except StopIteration:
            return []

    def delete_all_members(self):
        """Try to delete all members. Return False if one or more delete
        attempts raised an error."""

        def internal():
            for member in self.members():
                try:
                    member.delete()
                    yield True
                except api.CommunicationError:
                    yield False

        return all(list(internal()))

    ##
    # Miscellaneous
    ##

    def is_implemented(self):
        """Check whether a MailingList with this address is implemented by
        trying to load it from Mailgun."""

        try:
            self.__class__.load(self.address)
        except self.MailingListNotLoadable:
            return False
        else:
            return True
