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
        pytest.fail()

    @responses.activate
    def test_load(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass

    def test_implement(self):
        pass

    def test_is_implemented(self):
        pass
