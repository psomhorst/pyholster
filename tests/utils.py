import os
import yaml
import json


def load_fixture(filename):
    path = os.path.join(os.path.dirname(__file__), 'fixtures/', filename)
    with open(path, 'r') as stream:
        if filename.endswith('yml'):
            return yaml.load(stream)
        elif filename.endswith('json'):
            return json.load(stream)
        raise ValueError("Filename should end with '.yml' or '.json'.")
