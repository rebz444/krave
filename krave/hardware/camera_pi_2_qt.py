from PyQt5 import QtCore, QtWidgets
from picamera2 import Picamera2, Preview

import time


class CameraPi:
    def __init__(self):
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(main={"size": (512, 600)})
        self.picam.configure(config)
        self.camera_on = False
        self.preview = None

    def on(self):
        self.preview = self.picam.start_preview(Preview.QTGL)
        print("Preview object:", self.preview)  # Check if preview object is created
        self.preview.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.preview.setGeometry(100, 100, 600, 600)
        self.preview.show()
        print("Preview shown")  # Check if show() is called
        self.picam.start()
        self.camera_on = True

    def off(self):
        if self.camera_on:
            self.preview.close()
            self.camera_on = False

    def shutdown(self):
        self.off()
        self.picam.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    camera = CameraPi()
    camera.on()
    time.sleep(10)  # Uncomment for testing
    camera.shutdown()
    app.exec_()