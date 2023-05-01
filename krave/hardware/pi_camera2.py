from picamera2 import Picamera2, Preview
# import time

# picam2 = Picamera2()
# picam2.start_preview(Preview.QTGL, x=0, y=0, width=512, height=600)
# picam2.start()
# time.sleep(20)
# picam2.stop_preview()


class CameraPi:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.start_preview(Preview.QTGL)

    def on(self):
        self.picam2.start()

    def off(self):
        self.picam2.stop_preview()



