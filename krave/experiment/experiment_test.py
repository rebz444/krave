import time

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.camera_trigger import CameraTrigger
from krave.output.data_writer import DataWriter


class Session:
    def __init__(self, mouse, exp_name):
        self.mouse = mouse
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']

        self.spout = Spout(self.mouse, self.exp_config, spout_name="1", duration=0.08)
        self.visual = Visual(self.mouse, self.exp_config)
        self.data_writer = DataWriter(self.mouse, self.exp_config)
        self.camera_trigger = CameraTrigger(self.mouse, self.exp_config)

        self.session_length = self.exp_config['session_length']  # number of blocks per session
        self.block_length = self.exp_config['block_length']  # number of trials per block

        self.n_block = 0
        self.session_start_time = None
        self.running = False

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def start(self):
        self.session_start_time = time.time()
        self.running = True

    def run(self):
        self.camera_trigger.square_wave(self.data_writer)
        for n_block in range(self.session_length):
            if n_block//2 == 0:
                time_bg = 1
            else:
                time_bg = 3
            block = Block(self.visual, self.spout, self.data_writer, self.block_length, time_bg)
            block.run()
            self.n_block += 1

    def end(self):
        self.running = False
        self.spout.shutdown()
        self.visual.shutdown()
        self.data_writer.end()


class Block:
    def __init__(self, visual, spout, data_writer, block_length, time_bg):
        self.visual = visual
        self.spout = spout
        self.data_writer = data_writer

        self.block_length = block_length
        self.time_bg = time_bg

        self.block_start_time = time.time()

    def run(self):
        for n_trial in range(self.block_length):
            trial = Trial(self.visual, self.spout, self.data_writer, self.time_bg)
            trial.run()
            n_trial += 1


class Trial:
    def __init__(self, visual, spout, data_writer, time_bg):
        self.visual = visual
        self.spout = spout
        self.data_writer = data_writer

        self.trial_start_time = time.time()
        self.time_bg = time_bg
        self.trial_start_time = time.time()

    def run(self):
        while self.trial_start_time + self.time_bg > time.time():
            self.spout.water_cleanup()
            lick_change = self.spout.lick_status_check()
        if self.trial_start_time + self.time_bg - time.time() < 0.01:
            self.visual.cue_on()







