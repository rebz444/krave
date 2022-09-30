import time
import os

from krave import utils

from pypylon import pylon
import numpy as np
import cv2


def time_elapsed(prev=0):
    t = time.perf_counter()
    if prev == 0:
        return t
    else:
        print(f'Executed in {t - prev:0.4f} seconds')
        return t


class Camera:
    def __init__(self, exp_name, hardware_config_name, mouse):
        self.mouse = mouse
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', '../hardware/hardware.json')[hardware_config_name]

        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.frame_rate = self.hardware_config["frame_rate"]
        self.exposure_time = self.hardware_config["exposure_time"]
        self.frame_width = self.hardware_config["frame_width"]
        self.frame_height = self.hardware_config["frame_height"]
        self.OffsetX = self.hardware_config["OffsetX"]
        self.OffsetY = self.hardware_config["OffsetY"]

        self.datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = "camera_data_" + self.datetime + ".txt"
        self.data_write_path = '/camera_data/' + self.mouse + '_' + self.datetime

        self.start_time = 0
        self.current_time = 0
        self.time_btw_frame = 1/self.frame_rate
        print(self.time_btw_frame)
        self.frame_count = 0
        self.t = []
        self.images = []

    def initialize(self):
        self.camera.Open()
        self.camera.UserSetSelector = "Default"
        self.camera.ExposureTime.SetValue(self.exposure_time)
        print(f'exposure time: {self.exposure_time}')
        self.camera.Width = self.frame_width
        self.camera.Height = self.frame_height
        self.camera.OffsetX = self.OffsetX
        self.camera.OffsetY = self.OffsetY
        self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)

    def check_frame(self, start_time):
        self.current_time = time.time() - start_time
        if self.current_time > self.frame_count * self.time_btw_frame:
            grab = self.camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
            if grab and grab.GrabSucceeded():
                # cv2.imwrite(f'img_{self.frame_count}.jpeg', grab.Array)
                self.images.append(grab.Array)
                grab.Release()
                self.frame_count += 1
                return self.current_time
            else:
                return None
        else:
            return None

    def shutdown(self, folder_name):
        self.camera.StopGrabbing()
        for i, img in enumerate(self.images):
            cv2.imwrite(f'img_{i}.jpeg', img)
        self.camera.Close()

    def record_2(self, time_limit):
        print(os.getcwd())
        os.system('sudo -u pi mkdir -p ' + os.getcwd() + self.data_write_path)  # make dir for data write path
        os.chdir(os.getcwd() + self.data_write_path)

        num_frames = int(time_limit * self.frame_rate)
        self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
        self.start_time = time.time()
        while self.camera.IsGrabbing():
            self.current_time = time.time() - self.start_time
            if self.current_time > self.frame_count * self.time_btw_frame:
                self.frame_count += 1
                print(self.current_time)
                grab = self.camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
                if grab and grab.GrabSucceeded():
                    self.t.append(self.current_time)
                    self.images.append(grab.GetArray())
            if self.frame_count >= num_frames:
                self.camera.StopGrabbing()

    def shutdown_2(self):
        for i, img in enumerate(self.images):
            cv2.imwrite(f'img_{i}.jpeg', img)
        np.savetxt(self.filename, self.t, delimiter=',')
        self.camera.Close()

    def speed_test(self, frames):
        t = []
        self.start_time = time.time()
        while self.camera.IsGrabbing():
            grab = self.camera.RetrieveResult(100, pylon.TimeoutHandling_ThrowException)
            if grab and grab.GrabSucceeded():
                self.frame_count += 1
                t.append(grab.TimeStamp)
                img = grab.GetArray()
                cv2.imwrite(f'test_{self.frame_count}.jpeg', img)
            if self.frame_count == frames:
                break
        print(f'Acquired {self.frame_count} frames in {time.time() - self.start_time:.0f} seconds')
        np.savetxt(self.filename, t, delimiter=',')
        self.camera.Close()

    def shutdown_1(self):
        self.camera.Close()


if __name__ == '__main__':
    camera = Camera('exp1', 'setup1', 'RZ001')
    camera.initialize()
    camera.speed_test(100)
    camera.shutdown_1()
