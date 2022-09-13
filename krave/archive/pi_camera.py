import time

from picamera import PiCamera


class Camera_Pi:
    def __init__(self):
        self.camera_pi = PiCamera()
        self.camera_pi.resolution = (640, 480)

    def camera_test(self, video_name, video_length):
        self.camera_pi.start_preview()
        time.sleep(2)
        self.camera_pi.stop_preview()

        self.camera_pi.start_recording(f"{video_name}.h264")
        print(video_name)
        time.sleep(video_length)
        self.camera_pi.stop_recording()

        self.camera_pi.close()


