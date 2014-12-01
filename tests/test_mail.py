import responses
import pyholster as ph
import pytest


class TestMail:

    def test_init(self):
        mail = ph.Mail(sender="foo@bar.baz",
                       cc="foobar@baz.bar")

        assert mail.sender == "foo@bar.baz"
        assert mail.cc == "foobar@baz.bar"

        with pytest.raises(AttributeError):
            ph.Mail(id='test')

    def test_get_data(self):
        data = dict(sender="foo@bar.baz",
                    domain="testdomain.co.uk",
                    to="recipient@recipients.thus",
                    subject="This is a subject.",
                    text="Random text.")
        mail = ph.Mail(**data)

        data['from'] = data['sender']
        del data['sender']
        del data['domain']

        assert mail.get_data() == data

    def test_get_files(self):
        data = dict(subject="This is subject.",
                    to="foo@bar.baz",
                    domain="thus",
                    message="MIME")
        mail = ph.Mail(**data)
        assert mail.get_files() == {'message': "MIME"}

        data = dict(subject="This is subject.",
                    to="foo@bar.baz",
                    domain="thus",
                    text="Random text",
                    attachments=["test", "test2"])
        mail = ph.Mail(**data)
        assert mail.get_files() == [('attachment', "test"), ('attachment', "test2")]

    def test_send(self):
        pass

    def test_check_attributes(self):
        pass
