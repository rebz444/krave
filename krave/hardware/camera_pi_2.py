from picamera2 import Picamera2, Preview

import time


class CameraPi:
    def __init__(self):
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(main={"size": (512, 600)},
                                                         display="lores")
        self.picam.configure(config)
        self.camera_on = False

    def on(self):
        self.picam.start_preview(Preview.QTGL)
        # self.picam.set_controls({"qt-preview-window": (0, 0)})
        # self.picam.set_controls({"qt-preview-window-size": (512, 600)})
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