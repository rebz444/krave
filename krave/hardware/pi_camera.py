import time

from picamera import PiCamera


class Camera_Pi:
    def __init__(self):
        self.camera_pi = PiCamera()
        self.camera_pi.resolution = (640, 480)

    def camera_on(self):
        self.camera_pi.start_preview()

    def camera_shutdown(self):
        self.camera_pi.stop_preview()
        self.camera_pi.close()

