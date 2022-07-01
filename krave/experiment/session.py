import logging
import time

from krave import utils
from krave.output.data_writer import DataWriter
from krave.experiment.block import BlockDefault, BlockExp2
from krave.hardware.visual import Visual
from krave.hardware.spout import Spout


class Session:
    def __init__(self, info):
        self.info = info
        self.exp_name = info.exp_name
        self.mouse = info.mouse
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_name]

        self.spout = Spout(self.exp_name, self.hardware_name, "1")
        self.visual = Visual(self.exp_name, self.hardware_name)
        self.data_writer = DataWriter(self.exp_name, self.hardware_name, self.info)
        # self.blocks = self.get_blocks()

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def get_blocks(self):
        block_list = list()
        if self.exp_config["block_type"] == "default":
            block_object = BlockDefault
        elif self.exp_config["block_type"] == "exp2":
            block_object = BlockExp2
        for block_config in self.exp_config["blocks"]:
            block_list.append(block_object(self.exp_config, block_config))
        return block_list

    def get_trials(self):
        """Get list of trials from config."""
        pass

    def shutdown(self):
        self.spout.shutdown()
        self.visual.shutdown()
        return time.time()

    def run(self):
        """Run experiment."""
        logging.info(f"Starting session for experiment {self.exp_name}")
        self.spout.initialize()
        self.visual.initialize()
        for block in self.blocks:
            block.run(self.spout, self.visual, self.data_writer)
        self.shutdown()



