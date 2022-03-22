import logging
import time

from krave.experiment.block import BlockDefault, BlockExp2
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.lick import Lick
from krave import utils


class Session:
    def __init__(self, exp_name):
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        # dict of session config
        self.spout = Spout(self.exp_name, self.hardware_name)
        self.visual = Visual(self.exp_name, self.hardware_name)
    #     self.lick = Lick(self.exp_config['hardware_setup'])
    #     self.visual = Visual(self.exp_config)
    #     # self.data_writer = DataWriter(self.config_name)
    #     # self.blocks = self.get_blocks()

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def test_spout(self):
        self.spout.test_spout()

    # def get_blocks(self):
    #     block_list = list()
    #     if self.exp_config["block_type"] == "default":
    #         block_object = BlockDefault
    #     elif self.exp_config["block_type"] == "exp2":
    #         block_object = BlockExp2
    #     for block_config in self.exp_config["blocks"]:
    #         block_list.append(block_object(self.exp_config, block_config))
    #     return block_list
    #
    # def get_trials(self):
    #     """Get list of trials from config."""
    #     pass
    #
    # def run(self):
    #     """Run experiment."""
    #     logging.info(f"Starting session for experiment {self.exp_name}")
    #     self.water.initialize()
    #     self.lick.initialize()
    #     self.visual.initialize()
    #     for block in self.blocks:
    #         block.run(self.water, self.lick, self.visual, self.data_saver)
    #     self.shutdown()
    #
    # def test_visual_cue(self):
    #     # self.visual.test_one_run()
    #     # self.visual.initialize()
    #     # self.visual.test_cue()
    #     self.visual.main_loop()
    #     # self.visual.cue_on()
    #     # self.visual.cue_off()
    #     # time.sleep(5)
    #
    #
    #
