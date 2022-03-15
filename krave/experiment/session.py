import logging
import time

from krave.experiment.block import BlockDefault, BlockExp2
from krave.hardware.water import Water
from krave.hardware.visual import Visual
from krave import utils


class Session:
    def __init__(self, config_name):
        self.config_name = config_name
        self.config = self.get_config()
        self.water = Water(self.config['hardware_setup'])
        self.visual = Visual(self.config)
        # self.data_writer = DataWriter(self.config_name)
        # self.blocks = self.get_blocks()

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.config_name}.json')

    def get_blocks(self):
        block_list = list()
        if self.config["block_type"] == "default":
            block_object = BlockDefault
        elif self.config["block_type"] == "exp2":
            block_object = BlockExp2
        for block_config in self.config["blocks"]:
            block_list.append(block_object(self.config, block_config))
        return block_list

    def get_trials(self):
        """Get list of trials from config."""
        pass

    def run(self):
        """Run experiment."""
        logging.info(f"Starting session for experiment {self.config_name}")
        self.water.initialize()
        self.lick.initialize()
        self.visual.initialize()
        for block in self.blocks:
            block.run(self.water, self.lick, self.visual, self.data_saver)
        self.shutdown()

    def test_visual_cue(self):
        self.visual.initialize()
        time.sleep(5)
        self.visual.cue_on()
        self.visual.cue_off()
        time.sleep(5)

    def test_pi(self):
        print("poop")
