# import RPi.GPIO as GPIO
import time


class Water:
    def __init__(self):
        self.water_opened_time = None
        self.water = False

    def water_on(self):
        """turn on water, and return time turned on"""
        GPIO.output(self.water_pin, GPIO.HIGH)
        self.water = True
        self.water_opened_time = time.time()
        return time.time()

    def water_off(self):
        """turn off water, and return time turned off"""
        GPIO.output(self.water_pin, GPIO.HIGH)
        self.water = False
        return time.time()

    def water_cleanup(self):
        if self.water and self.water_opened_time + self.base_durations < time.time():
            pass
