import time

from krave import utils

import RPi.GPIO as GPIO
from pypylon import pylon

GPIO.setmode(GPIO.BCM)


class Camera:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.camera_pin = self.hardware_config['camera']
        GPIO.setup(self.camera_pin, GPIO.OUT)
        self.start_time = time.time()
        self.frame_rate = 30
        self.last_frame = 0

    def independent_test(self, run_time):
        current_time = time.time()
        while current_time-self.start_time < run_time:
            current_time = time.time()
            if current_time-self.last_frame > 1/self.frame_rate:
                self.last_frame = current_time
                GPIO.output(self.camera_pin, GPIO.HIGH)
            elif current_time-self.last_frame > 1/self.frame_rate/2:
                GPIO.output(self.camera_pin, GPIO.LOW)

    def test_test(self):
        for i in range(1000):
            GPIO.output(self.camera_pin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(self.camera_pin, GPIO.LOW)
            time.sleep(1)
        GPIO.cleanup()
        print("GPIO cleaned up")


if __name__ == '__main__':
    camera = Camera('exp1', 'setup1')
    camera.test_test()