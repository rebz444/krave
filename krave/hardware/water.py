# import RPi.GPIO as GPIO
import time

from krave import utils


class Water:
    def __init__(self, hardware_config_name):
        self.water_opened_time = None
        self.water = False
        self.base_duration = 1
        self.config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        print(self.config)

    def water_on(self):
        """turn on water, and return time turned on"""
        GPIO.output(self.config['water_output'], GPIO.HIGH)
        self.water = True
        self.water_opened_time = time.time()
        return time.time()

    def water_off(self):
        """turn off water, and return time turned off"""
        GPIO.output(self.config['water_output'], GPIO.HIGH)
        self.water = False
        return time.time()

    def water_cleanup(self):
        if self.water and self.water_opened_time + self.base_durations < time.time():
            pass