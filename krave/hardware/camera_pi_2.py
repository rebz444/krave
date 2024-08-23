from picamera2 import Picamera2, Preview

import time
import os


class CameraPi:
    def __init__(self):
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(main={"size": (512, 600)})
        self.picam.configure(config)
        self.camera_on = False

    def on(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        self.picam.start_preview(Preview.QTGL)
        self.picam.start()
        self.camera_on = True

    def off(self):
        self.picam.stop_preview()
        self.camera_on = False

    def shutdown(self):
        self.off()
        self.picam.stop()


if __name__ == '__main__':
    camera = CameraPi()
    camera.on()
    time.sleep(10)
    camera.shutdown()