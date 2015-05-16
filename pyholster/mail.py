import json

from . import api


class Mail(object):

    """Handles the sending of a Mail trough Mailgun."""

    id = None
    sent = False

    sender = None
    to = None
    cc = None
    bcc = None
    subject = None
    text = None
    html = None
    message = None
    attachments = None
    inline = None
    options = None
    headers = None
    variables = None

    def __init__(self, **kwargs):
        """Initialize a Mail object."""

        args = ('domain',
                'sender',
                'to', 'cc', 'bcc',
                'subject',
                'text', 'html', 'message',
                'attachments', 'inline',
                'options', 'headers', 'variables')

        unknown_attrs = set(kwargs.keys()) - set(args)

        if len(unknown_attrs):
            raise AttributeError(
                "Unknown attributes {}.".format(', '.join(unknown_attrs)))

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def send(self):
        """Send the Mail to Mailgun."""

        self.check_attributes()
        data = self.get_data()
        files = self.get_files()

        url = ('/{}/messages.mime' if self.message
               else '/{}/messages').format(self.domain)

        response = api.post(url, data, files=files)

        if response['message'] == "Queued. Thank you.":
            self.id = response.get('id')
            self.sent = True
            return True

        else:
            raise errors.MailgunException(
                "Could not send message: {}".format(response.message))

    def get_data(self):
        """Create a data structure."""

        data = {}

        for attr in (x for x in ('to', 'cc', 'bcc', 'subject',
                                 'text', 'html') if getattr(self, x)):
            data[attr] = getattr(self, attr)

        data['from'] = self.sender

        for attr in (x for x in ('options', 'headers') if getattr(self, x)):
            for key, value in getattr(self, attr).iteritems():
                data['{}:{}'.format(attr[0], key)] = value

        if self.variables:
            for key, value in self['variables'].iteritems():
                data['v:{}'.format(key)] = json.dumps(value)

        return data

    def get_files(self):
        """Create a file structure."""

        if self.message:
            return {'message': self.message}
        elif self.attachments:
            return [('attachment', attachment)
                    for attachment in self.attachments]
        else:
            return None

    def check_attributes(self):
        """Check whether the attributes are the right format."""


        if not any(bool(x) for x in [self.text, self.message, self.html]):
            raise ValueError(
                "Either 'text', 'html' or 'message' should be set.")
        if any([self.text, self.html]) and self.message:
            raise ValueError("Either 'message' should be set, or 'test' and/or 'html',"
                             " not both 'message' and 'text'/'html'.")

        if not self.domain:
            raise ValueError("'domain' should be set.")
        if not self.sender and not self.message:
            raise ValueError("'sender' should be set.")
        if not any([self.to, self.cc, self.bcc]):
            raise ValueError("'to', 'cc' and/or 'bcc' should be set.")
        if not self.subject and not self.message:
            raise Warning("'subject' should be set.")

        if self.attachments and self.message:
            raise ValueError("'attachments' and 'message' cannot both be set.")

        return True
