import time

from krave import utils

import RPi.GPIO as GPIO
import numpy as np


class Reward:
    def __init__(self, exp_config, spout_name):
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]
        self.lick_pin = self.hardware_config['spouts_pump'][spout_name][0]
        self.pump_pin_1 = self.hardware_config['spouts_pump'][spout_name][1]
        self.pump_pin_2 = self.hardware_config['spouts_pump'][spout_name][2]
        self.pump_pin_3 = self.hardware_config['spouts_pump'][spout_name][3]

        self.calibration_config = utils.get_config('krave.hardware', 'pump_calibration.json')
        self.ul_per_turn = self.calibration_config['ul_per_turn']
        self.pump_pulse_to_turns = self.calibration_config['pump_pulse_to_turns']
        self.pin_for_reward = self.calibration_config['pin_for_reward']

        self.frequency = 50
        self.interval = 1/self.frequency
        self.last_high = None
        self.high = False
        self.high_times = []
        self.low_times = []

        self.lick_status = 0
        self.lick_record = np.ones([2])
        self.num_pulses = 0
        self.water_dispensing = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lick_pin, GPIO.IN)
        GPIO.setup(self.pump_pin_1, GPIO.OUT)
        GPIO.setup(self.pump_pin_2, GPIO.OUT)
        GPIO.setup(self.pump_pin_3, GPIO.OUT)
        GPIO.output(self.pump_pin_1, GPIO.LOW)
        GPIO.output(self.pump_pin_2, GPIO.LOW)
        GPIO.output(self.pump_pin_3, GPIO.LOW)

    def lick_status_check(self):
        """register change only when current status is different than all two previous status"""
        self.lick_record = np.roll(self.lick_record, 1)
        print(self.lick_record)
        self.lick_record[0] = GPIO.input(self.lick_pin)
        change_bool = np.all(self.lick_record != self.lick_status)
        change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        self.lick_status += change
        return change

    def calculate_pulses(self, reward_size_ul):
        self.num_pulses = round(reward_size_ul / (self.ul_per_turn * self.pump_pulse_to_turns[self.pin_for_reward - 1]))

    def one_pulse(self):
        if (time.time() - self.last_high) > self.interval:
            GPIO.output(self.pin_for_reward, GPIO.HIGH)
            self.last_high = time.time()
            self.high = True
        if (time.time() - self.last_high) > self.interval / 2 and self.high:
            GPIO.output(self.pin_for_reward, GPIO.LOW)
            self.high = False

    # def calculate_pulse_times(self):
    #     self.pulse_start_time = time.time()
    #     self.high_times =

    def shutdown(self):
        GPIO.output(self.pump_pin_1, GPIO.LOW)
        GPIO.output(self.pump_pin_2, GPIO.LOW)
        GPIO.output(self.pump_pin_3, GPIO.LOW)
        self.water_dispensing = False

