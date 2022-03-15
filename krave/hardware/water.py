import RPi.GPIO as GPIO
import time

from krave import utils


class Water:
    def __init__(self, hardware_config_name):
        self.config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.base_durations = 1
        self.water_opened_time = None
        self.water_dispensing = False

    def water_on(self):
        """turn on water, and return time turned on"""
        GPIO.output(self.config['water_output'], GPIO.HIGH)
        self.water_dispensing = True
        self.water_opened_time = time.time()
        return time.time()

    def water_off(self):
        """turn off water, and return time turned off"""
        GPIO.output(self.config['water_output'], GPIO.HIGH)
        self.water_dispensing = False
        return time.time()

    def water_cleanup(self):
        if self.water_dispensing and self.water_opened_time + self.base_durations < time.time():
            pass