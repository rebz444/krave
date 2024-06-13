import time

import RPi.GPIO as GPIO
import numpy as np


class Spout:
    def __init__(self, hardware_config, data_writer):
        self.data_writer = data_writer
        self.lick_pin = hardware_config['lick']
        self.lick_rolling = hardware_config['lick_rolling']  # roll lick records to avoid sensor flickering
        self.pump_pins = [hardware_config['pump'], hardware_config['pump_to_box']]
        # pin number used for reward, and pin number used to sync to NI box
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

    def lick_status_check(self, status):
        """
        Checks for changes in lick sensor status and updates internal state.
        Returns:
            int: 1 if lick detected, -1 if lick stopped, 0 if no change.
        """
        if self.lick_rolling:
            self.lick_record = np.roll(self.lick_record, 1)
            self.lick_record[0] = GPIO.input(self.lick_pin)
            change_bool = np.all(self.lick_record != self.lick_status)
            change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        else:
            change = GPIO.input(self.lick_pin) - self.lick_status

        self.lick_status += change
        self.log_lick(status, change)

        return change

    def log_lick(self, status, change):
        if change == 1:
            self.data_writer.log(status + 'nan,1,lick')
        elif change == -1:
            self.data_writer.log(status + 'nan,0,lick')
        else:
            pass

    def calculate_pulses(self, reward_size_ul, status):
        self.num_pulses = round(reward_size_ul / (self.ul_per_turn * self.pump_pulse_to_turns))
        print(f'delivering {self.num_pulses} pulses')
        self.data_writer.log(status + 'nan,1,reward')
        return self.num_pulses

    def send_continuous_pulse(self, status):
        if (time.time() - self.last_pulse_time) > self.interval and not self.high:
            for pin in self.pump_pins:
                GPIO.output(pin, GPIO.HIGH)
            self.data_writer.log(status + 'nan,1,pump')
            self.last_pulse_time = time.time()
            self.high = True
        if (time.time() - self.last_pulse_time) > self.interval / 2 and self.high:
            for pin in self.pump_pins:
                GPIO.output(pin, GPIO.LOW)
            self.data_writer.log(status + 'nan,0,pump')
            self.high = False
            self.num_pulses -= 1

    def send_single_pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.interval / 2)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(self.interval / 2)

    def water_cleanup(self, status):
        if self.num_pulses > 0:
            self.water_dispensing = True
            self.send_continuous_pulse(status)
        elif self.num_pulses == 0:
            self.water_dispensing = False

    def calibrate(self):
        print(f"{self.calibration_repeats} tubes needed for calibration")
        for _ in range(self.calibration_repeats):
            input(f"get tube ready, press Enter to start dispensing water ..")
            for _ in range(self.calibration_num_pulses):
                self.send_single_pulse(self.pump_pins[0])

    def shutdown(self):
        self.water_dispensing = False
        for pin in self.pump_pins:
            GPIO.output(pin, GPIO.LOW)


