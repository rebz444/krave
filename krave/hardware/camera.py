import time
import os

from krave import utils

# import RPi.GPIO as GPIO
from pypylon import pylon
import cv2

# GPIO.setmode(GPIO.BCM)


class Camera:
    def __init__(self, exp_name, hardware_config_name, mouse, exposure_time=8170):
        self.mouse = mouse
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.exposure_time = exposure_time
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.data_write_path = '/data/' + self.mouse
        self.start_time = 0
        self.frame_count = 0

        # self.camera_pin = self.hardware_config['camera']
        # GPIO.setup(self.camera_pin, GPIO.OUT)
        # self.frame_rate = 30
        # self.last_frame = 0

    def initialize(self):
        self.camera.Open()
        self.camera.UserSetSelector = "Default"
        self.camera.ExposureTime.SetValue(self.exposure_time)
        print(f'exposure time: {self.exposure_time}')

    def record_test(self):
        print(os.getcwd())
        os.system('sudo -u pi mkdir -p ' + os.getcwd() + self.data_write_path)  # make dir for data write path
        os.chdir(os.getcwd() + self.data_write_path)

        self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
        self.frame_count = 0
        t = []
        self.start_time = time.time()
        while self.camera.IsGrabbing():
            grab = self.camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
            if grab and grab.GrabSucceeded():
                self.frame_count += 1
                t.append(grab.TimeStamp)
                img = grab.GetArray()
                cv2.imwrite(f'test_{self.frame_count}.jpeg', img)
            if self.frame_count == 1000:
                break
        print(f'Acquired {self.frame_count} frames in {time.time() - self.start_time:.0f} seconds')
        return t

    def shut_down(self):
        self.camera.Close()

    # def independent_test(self, run_time):
    #     current_time = time.time()
    #     while current_time-self.start_time < run_time:
    #         current_time = time.time()
    #         if current_time-self.last_frame > 1/self.frame_rate:
    #             self.last_frame = current_time
    #             GPIO.output(self.camera_pin, GPIO.HIGH)
    #         elif current_time-self.last_frame > 1/self.frame_rate/2:
    #             GPIO.output(self.camera_pin, GPIO.LOW)


if __name__ == '__main__':
    camera = Camera('exp1', 'setup1')
    camera.initialize()
    camera.record_test()
    camera.shut_down()
