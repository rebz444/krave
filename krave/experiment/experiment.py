from pkg_resources import resource_string
import json

from krave.experiment.trial import Trial
from krave.experiment import constants as const
from krave.hardware.water import Water


class Experiment:
    def __init__(self, config_name):
        self._config = self.get_config(config_name)
        self.water = Water()

    def get_config(self, config_name):
        """Get experiment config from json"""
        return json.loads(resource_string('krave.experiment', f'config/{config_name}.json'))

    def get_trials(self):
        """Get list of trials from config."""
        pass

    def run(self):
        """Run experiment."""
        print("Hello World")