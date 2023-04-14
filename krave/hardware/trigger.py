import time

from krave import utils

import RPi.GPIO as GPIO


class Trigger:
    def __init__(self, hardware_config):
        self.camera_pin = hardware_config['camera']
        self.NI_box_pin = hardware_config['NI_box']
        self.frequency = hardware_config["trigger_frequency"]
        self.interval = 1 / self.frequency
        self.last_high = 0
        self.high = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.camera_pin, GPIO.OUT)
        GPIO.output(self.camera_pin, GPIO.LOW)
        GPIO.setup(self.NI_box_pin, GPIO.OUT)
        GPIO.output(self.NI_box_pin, GPIO.LOW)

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
            GPIO.output(self.NI_box_pin, GPIO.LOW)
            self.high = False
            string = 'nan,nan,nan,nan,nan,nan,0,square_wave'
            data_writer.log(string)

    def shutdown(self):
        GPIO.output(self.camera_pin, GPIO.LOW)
        GPIO.output(self.NI_box_pin, GPIO.LOW)
