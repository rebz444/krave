import time

import RPi.GPIO as GPIO
import numpy as np


class Spout:
    def __init__(self, hardware_config):
        self.lick_pin = hardware_config['spout']
        self.pump_pins = hardware_config['pump']  # list of pump pin numbers
        self.reward_pin_index = hardware_config['reward_pin_index']
        self.reward_pin = self.pump_pins[self.reward_pin_index]  # pin number used for reward
        self.pump_pulse_to_turns = hardware_config['pump_pulse_to_turns']
        self.ul_per_turn = hardware_config['ul_per_turn']
        self.interval = hardware_config['pump_pulse_interval']
        self.calibration_repeats = hardware_config['calibration_repeats']
        self.calibration_num_pulses = hardware_config['calibration_num_pulses']

        self.lick_status = 0
        self.lick_record = np.ones([2])

        self.last_pulse_time = 0
        self.high = False
        self.num_pulses = 0
        self.water_dispensing = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lick_pin, GPIO.IN)
        GPIO.setup(self.pump_pins, GPIO.OUT, initial=GPIO.LOW)

    def lick_status_check(self):
        """register change only when current status is different than all two previous status"""
        self.lick_record = np.roll(self.lick_record, 1)
        self.lick_record[0] = GPIO.input(self.lick_pin)
        change_bool = np.all(self.lick_record != self.lick_status)
        change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        self.lick_status += change
        return change

    def calculate_pulses(self, reward_size_ul):
        self.num_pulses = round(reward_size_ul / (self.ul_per_turn * self.pump_pulse_to_turns[self.reward_pin_index]))
        print(f'delivering {self.num_pulses} pulses')
        return self.num_pulses

    def send_continuous_pulse(self, pin):
        if (time.time() - self.last_pulse_time) > self.interval and not self.high:
            GPIO.output(pin, GPIO.HIGH)
            self.last_pulse_time = time.time()
            self.high = True
        if (time.time() - self.last_pulse_time) > self.interval / 2 and self.high:
            GPIO.output(pin, GPIO.LOW)
            self.high = False
            self.num_pulses -= 1

    def send_single_pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.interval/2)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(self.interval / 2)

    def cleanup(self):
        if self.num_pulses > 0:
            self.water_dispensing = True
            self.send_continuous_pulse(pin=self.reward_pin)
        elif self.num_pulses == 0:
            self.water_dispensing = False

    def calibrate(self):
        print(f"{len(self.pump_pins) * self.calibration_repeats} tubes needed for calibration")
        for pin in self.pump_pins:
            for _ in range(self.calibration_repeats):
                input(f"get tube ready, press Enter to start dispensing water ..")
                for _ in range(self.calibration_num_pulses):
                    self.send_single_pulse(pin)

    def shutdown(self):
        self.water_dispensing = False
        for pin in self.pump_pins:
            GPIO.output(pin, GPIO.LOW)


