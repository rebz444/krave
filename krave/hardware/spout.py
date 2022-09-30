import time
import numpy as np

from krave import utils

import RPi.GPIO as GPIO


class Spout:
    def __init__(self, mouse, exp_config, spout_name, duration):
        self.mouse = mouse
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]

        self.lick_pin = self.hardware_config['spouts'][spout_name][0]
        self.water_pin = self.hardware_config['spouts'][spout_name][1]

        self.lick_status = 0
        self.lick_record = np.ones([3])
        self.base_duration = duration
        self.water_opened_time = None
        self.water_dispensing = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lick_pin, GPIO.IN)
        GPIO.setup(self.water_pin, GPIO.OUT)
        GPIO.output(self.water_pin, GPIO.LOW)

    def lick_status_check(self):
        """register change only when current status is different than all three
        previous status"""
        self.lick_record = np.roll(self.lick_record, 1)
        self.lick_record[0] = GPIO.input(self.lick_pin)
        change_bool = np.all(self.lick_record != self.lick_status)
        change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        self.lick_status += change
        return change

    def water_on(self):
        """turn on water, return time turned on"""
        GPIO.output(self.water_pin, GPIO.HIGH)
        self.water_dispensing = True
        self.water_opened_time = time.time()
        return time.time()

    def water_off(self):
        """turn off water, and return time turned off"""
        GPIO.output(self.water_pin, GPIO.LOW)
        self.water_dispensing = False
        return time.time()

    def water_cleanup(self):
        if self.water_dispensing and self.water_opened_time + self.base_duration < time.time():
            duration = time.time() - self.water_opened_time
            GPIO.output(self.water_pin, GPIO.LOW)
            self.water_dispensing = False
            return duration

    def shutdown(self):
        self.water_off()
        GPIO.cleanup()
        print("GPIO cleaned up")
        return time.time()

