import time

from krave import utils

import RPi.GPIO as GPIO


class CameraTrigger:
    def __init__(self, mouse, exp_config):
        self.mouse = mouse
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]

        self.camera_pin = self.hardware_config['camera']
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.camera_pin, GPIO.OUT)

        self.frame_rate = self.hardware_config["frame_rate"]
        self.frame_interval = 1 / self.frame_rate
        self.last_frame = 0
        self.cam_high = False

    def square_wave(self, data_writer):
        if (time.time() - self.last_frame) > self.frame_interval:
            GPIO.output(self.camera_pin, GPIO.HIGH)
            self.last_frame = time.time()
            self.cam_high = True
            string = 'nan,nan,nan,nan,nan,nan,1,camera'
            data_writer.log(string)
        if (time.time() - self.last_frame) > self.frame_interval / 2 and self.cam_high:
            GPIO.output(self.camera_pin, GPIO.LOW)
            self.cam_high = False
            string = 'nan,nan,nan,nan,nan,nan,0,camera'
            data_writer.log(string)

