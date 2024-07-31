import time

import RPi.GPIO as GPIO


class CameraBasler:
    def __init__(self, hardware_config, data_writer):
        self.data_writer = data_writer
        self.camera_pins = [hardware_config['camera'], hardware_config['camera_to_box']]
        # [pin number used for camera, and pin number used to sync to NI box]
        self.interval = 1 / hardware_config["camera_frequency"]
        self.last_high = 0
        self.high = False

        GPIO.setmode(GPIO.BCM)
        for pin in self.camera_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def square_wave(self, status):
        if (time.time() - self.last_high) > self.interval and not self.high:
            for pin in self.camera_pins:
                GPIO.output(pin, GPIO.HIGH)
            self.last_high = time.time()
            self.high = True
            self.data_writer.log(status + 'nan,1,trigger')
        if (time.time() - self.last_high) > self.interval / 2 and self.high:
            for pin in self.camera_pins:
                GPIO.output(pin, GPIO.LOW)
            self.high = False
            self.data_writer.log(status + 'nan,0,trigger')

    def shutdown(self):
        for pin in self.camera_pins:
            GPIO.output(pin, GPIO.LOW)



