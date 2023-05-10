from picamera2 import Picamera2, Preview
from libcamera import controls

import time

# picam2 = Picamera2()
# config = picam2.create_preview_configuration(lores={})
# picam2.start(show_preview=True)
# # picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
# picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})
# time.sleep(10)
# picam2.stop_preview()
# picam2.stop()


# picam2 = Picamera2()
# picam2.preview_configuration.enable_lores()
# picam2.preview_configuration.lores.size = (320, 240)
# picam2.configure("preview")
# picam2.start(show_preview=True)
# picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})
# time.sleep(10)
# picam2.stop_preview()
# picam2.stop()

class CameraPi:
    def __init__(self):
        self.picam2 = Picamera2()
        self.config = self.picam2.create_preview_configuration(lores={})
        self.picam2.start(show_preview=True)
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})

    def on(self):
        self.picam2.start(show_preview=True)
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})

    def off(self):
        self.picam2.stop_preview()

    def shutdown(self):
        self.off()
        self.picam2.stop()

    def test_camera(self):
        self.on()
        time.sleep(10)
        self.shutdown()


if __name__ == '__main__':
    CameraPi().test_camera()


