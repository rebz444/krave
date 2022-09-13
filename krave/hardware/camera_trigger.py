import time

from krave import utils

import RPi.GPIO as GPIO


class CameraTrigger:
    def __init__(self, exp_name, hardware_config_name, mouse):
        self.mouse = mouse
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]

        self.camera_pin = self.hardware_config['camera']
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.camera_pin, GPIO.OUT)

        self.frame_rate = self.hardware_config["frame_rate"]
        self.frame_interval = 1 / self.frame_rate
        self.last_frame = time.time()
        self.cam_high = False

    def square_wave(self, data_writer):
        if (time.time() - self.last_frame) > self.frame_interval:
            GPIO.output(self.camera_pin, GPIO.HIGH)
            self.last_frame = time.time()
            self.cam_high = True
            string = f'nan,{self.last_frame},{1},camera'
            data_writer.log(string)
        if (time.time() - self.last_frame) > self.frame_interval / 2 and self.cam_high:
            GPIO.output(self.camera_pin, GPIO.LOW)
            img_off_time = time.time()
            self.cam_high = False
            string = f'nan,{img_off_time},{0},camera'
            data_writer.log(string)

