# import RPi.GPIO as GPIO
import time

from krave import utils


class Spout:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]

        self.spout_pins = self.hardware_config['spouts']
        # self.reward_distribution = self.exp_config['reward_distribution']
        #
        # self.base_duration = None
        # self.water_opened_time = None
        # self.water_dispensing = False

    def test_spout(self):
        print(self.spout_pins['1'][0])

    def initialize_spout(self):
        GPIO.setmode(GPIO.BCM)
        for spout in self.spout_pins:
            lick_pin = self.spout_pins[spout][0]
            water_pin = self.spout_pins[spout][1]
            GPIO.setup(lick_pin, GPIO.IN)
            GPIO.setup(water_pin, GPIO.OUT, initial=GPIO.LOW)

    def licked(self):
        change = GPIO.input

#     def reward_rate(self):
#         if self.reward_distribution == "delay1":
#             self.base_duration = 1
#             return self.base_duration
#
#
#     def initialize_water(self):
#         GPIO.setmode(GPIO.BCM)
#         for pin in self.water_pin:
#             GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
#
#     def on(self):
#         """turn on water, and return time turned on"""
#         GPIO.output(self.water_pin, GPIO.HIGH)
#         self.water_dispensing = True
#         self.water_opened_time = time.time()
#         return time.time()
#
#     def off(self):
#         """turn off water, and return time turned off"""
#         GPIO.output(self.water_pin, GPIO.LOW)
#         self.water_dispensing = False
#         return time.time()
#
#     def water_cleanup(self):
#         if self.water_on and self.water_opened_time + self.base_duration < time.time():
#             duration = time.time() - self.water_opened_time
#             GPIO.output(self.water_pin, GPIO.LOW)
#             self.water_dispensing = False
#             return duration
#
#
# class Lick:
#     def __init__(self, hardware_config_name):
#         self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
#         self.spout = self.hardware_config['lick_input']
#         self.spout_status = [0 for i in self.spout]
#
#     def initialize(self):
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.spout, GPIO.IN)  # check if low means no lick
#
#     def licked(self):
#         new_spout_status = GPIO.input(self.spout)
#
#         for old, new in zip(self.spout_status, new_spout_status):
#             change = self.spout_status - new_spout_status[new]
#             self.spout_status[new] = new_spout_status[new]
#         return change
#
#     def cleanup(self):
#         GPIO.cleanup(self.spout)
