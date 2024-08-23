import picamera2
from picamera2 import Preview
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget  # Import base class
import time

class CameraPi:
    def __init__(self):
        self.picam2 = picamera2.Picamera2()
        self.config = self.picam2.create_preview_configuration(main={"size": (512, 600)})
        self.picam2.configure(self.config)
        self.camera_on = False
        self.preview_widget = None  # Create a placeholder for the preview widget

    def on(self):
        self.picam2.start_preview(Preview.QTGL)
        self.camera_on = True

    def off(self):
        if self.camera_on:
            self.picam2.stop_preview()
            self.camera_on = False

    def shutdown(self):
        self.off()
        self.picam2.stop()

    def create_preview_window(self):
        # Create a custom preview widget using PyQt5
        self.preview_widget = QWidget()  # Create a widget for the preview
        # Implement the logic to display the camera preview within this widget
        # This might involve creating a QLabel or subclassing QAbstractVideoSurface

    def run(self):
        app = QApplication([])
        camera = CameraPi()
        camera.on()

        camera.create_preview_window()  # Create the preview widget before showing window
        window = QMainWindow()
        window.setCentralWidget(camera.preview_widget)

        window.move(100, 100)
        window.show()
        app.exec_()

        camera.shutdown()

if __name__ == '__main__':
    camera = CameraPi()
    camera.run()  # Call the run method to start the application