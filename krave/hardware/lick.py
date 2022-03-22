# import RPi.GPIO as GPIO
import time

from krave import utils


class Lick:
    def __init__(self, hardware_config_name):
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.spout = self.hardware_config['lick_input']
        self.spout_status = [0 for i in self.spout]

    def initialize(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.spout, GPIO.IN)  # check if low means no lick

    def licked(self):
        new_spout_status = GPIO.input(self.spout)

        for old, new in zip(self.spout_status, new_spout_status):
            change = self.spout_status - new_spout_status[new]
            self.spout_status[new] = new_spout_status[new]
        return change

    def cleanup(self):
        GPIO.cleanup(self.spout)

