import time

from krave import utils

import RPi.GPIO as GPIO


class SyringePump:
    def __init__(self, exp_config):
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]
        self.pump_pin_1 = self.hardware_config['syringe_pump'][0]
        self.pump_pin_2 = self.hardware_config['syringe_pump'][1]
        self.pump_pin_3 = self.hardware_config['syringe_pump'][2]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pump_pin_1, GPIO.OUT)
        GPIO.setup(self.pump_pin_2, GPIO.OUT)
        GPIO.setup(self.pump_pin_3, GPIO.OUT)
        GPIO.output(self.pump_pin_1, GPIO.LOW)
        GPIO.output(self.pump_pin_2, GPIO.LOW)
        GPIO.output(self.pump_pin_3, GPIO.LOW)

    def pump_on(self):
        GPIO.output(self.pump_pin_1, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.pump_pin_1, GPIO.LOW)