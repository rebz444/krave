from picamera import PiCamera


class CameraPi:
    def __init__(self):
        self.camera_pi = PiCamera()
        self.camera_pi.resolution = (512, 600)
        self.camera_pi.preview_fullscreen = False
        self.camera_pi.preview_window = (0, 0, 512, 600)

    def on(self):
        self.camera_pi.start_preview()

    def off(self):
        self.camera_pi.stop_preview()

    def shutdown(self):
        self.off()
        self.camera_pi.close()


if __name__ == '__main__':
    CameraPi().shutdown()

