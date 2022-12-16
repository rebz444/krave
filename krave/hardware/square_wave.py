import time

from krave import utils

import RPi.GPIO as GPIO


class SquareWave:
    def __init__(self, mouse, exp_config):
        self.mouse = mouse
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]

        self.camera_pin = self.hardware_config['camera']
        self.NI_box_pin = self.hardware_config['NI_box']
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.camera_pin, GPIO.OUT)
        GPIO.output(self.camera_pin, GPIO.LOW)
        GPIO.setup(self.NI_box_pin, GPIO.OUT)
        GPIO.output(self.NI_box_pin, GPIO.LOW)

        self.frequency = self.hardware_config["frequency"]
        self.interval = 1 / self.frequency
        self.last_high = 0
        self.high = False

    def square_wave(self, data_writer):
        if (time.time() - self.last_high) > self.interval:
            GPIO.output(self.camera_pin, GPIO.HIGH)
            GPIO.output(self.NI_box_pin, GPIO.HIGH)
            self.last_high = time.time()
            self.high = True
            string = 'nan,nan,nan,nan,nan,nan,1,square_wave'
            data_writer.log(string)
        if (time.time() - self.last_high) > self.interval / 2 and self.high:
            GPIO.output(self.camera_pin, GPIO.LOW)
            self.high = False
            string = 'nan,nan,nan,nan,nan,nan,0,square_wave'
            data_writer.log(string)

