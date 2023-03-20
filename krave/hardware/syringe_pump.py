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

    def pump_pin_1_on(self):
        GPIO.output(self.pump_pin_1, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.pump_pin_1, GPIO.LOW)
        time.sleep(0.2)

    def pump_pin_2_on(self):
        GPIO.output(self.pump_pin_2, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.pump_pin_2, GPIO.LOW)
        time.sleep(0.2)

    def pump_pin_3_on(self):
        GPIO.output(self.pump_pin_3, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.pump_pin_3, GPIO.LOW)
        time.sleep(0.2)

    def calibrate_pump_pin_1(self):
        for _ in range(100):
            self.pump_pin_1_on()

    def calibrate_pump_pin_2(self):
        for _ in range(100):
            self.pump_pin_2_on()

    def calibrate_pump_pin_3(self):
        for _ in range(100):
            self.pump_pin_3_on()
