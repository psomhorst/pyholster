from dateutil import parser as dtparser

from . import api
from . import errors


class Route(object):

    priority = None
    description = None
    expression = None
    actions = None
    id = None
    created_at = None

    def __init__(self, **kwargs):
        try:
            print(kwargs.get('actions'), type(kwargs.get('actions')))
        except:
            pass

        if not isinstance(kwargs['actions'], list):
            raise ValueError("Actions should be a list.")

        object.__setattr__(self, 'expression', kwargs['expression'])
        object.__setattr__(self, 'actions', kwargs['actions'])
        object.__setattr__(self, 'priority', kwargs.get('priority', 0))
        object.__setattr__(self, 'description', kwargs.get('description', None))
        object.__setattr__(self, 'id', kwargs.get('id', None))
        object.__setattr__(self, 'created_at', (dtparser.parse(kwargs.get('created_at'))
                                                if 'created_at' in kwargs else None))

    def __setattr__(self, name, value):
        raise AttributeError(
            'The Route object cannot be altered directly. Use the update() method instead.')

    @classmethod
    def load(cls, id):
        try:
            response = api.get('/routes/{}'.format(id))
        except errors.MailgunException:
            raise LookupError('Could not load Route from Mailgun.')
        else:
            return cls(**response['route'])

    @classmethod
    def load_all(cls):
        try:
            response = api.get('/routes')
        except errors.MailgunException:
            raise LookupError('Could not load Routes from Mailgun.')
        else:
            return (cls(**m) for m in response['items'])

    def update(self, **kwargs):


        if not self.is_implemented():
            raise errors.MailgunException(
                'Cannot update non-implemented Route. Implement first.')

        if 'id' in kwargs:
            raise AttributeError('Cannot update the ID of a Route.')

        update_data = {}

        for key in set(kwargs.keys()) & set(['priority', 'description', 'expression']):
            object.__setattr__(self, key, kwargs[key])
            update_data[key] = kwargs[key]

        if 'actions' in kwargs:
            object.__setattr__(self, 'actions', kwargs['actions'])
            update_data['action'] = kwargs['actions']

        try:
            api.put('/routes/{}'.format(self.id), update_data)
        except errors.MailgunRequestException:
            raise
        else:
            return True

    def implement(self):
        if self.is_implemented():
            raise errors.MailgunException("This Route is already implemented.")

        data = {'priority': self.priority,
                'description': self.description,
                'expression': self.expression,
                'action': self.actions}

        try:
            api.post('/routes', data)
        except errors.MailgunRequestException:
            raise
        else:
            return True

    def delete(self):
        try:
            api.delete('/routes/{}'.format(self.id))
        except errors.MailgunRequestException:
            raise
        return True

    def is_implemented(self):
        if not self.id:
            return False
        try:
            self.__class__.load(self.id)
        except LookupError:
            return False
        else:
            return True
