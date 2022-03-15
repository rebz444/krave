import json
from pkg_resources import resource_string, resource_filename


def get_config(module, filename):
    return json.loads(resource_string(module, filename))


def get_path(module, filename):
    return resource_filename(module, filename)