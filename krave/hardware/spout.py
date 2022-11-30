import time

from krave import utils

import RPi.GPIO as GPIO
import numpy as np
from sklearn.linear_model import LinearRegression


class Spout:
    def __init__(self, mouse, exp_config, spout_name):
        self.mouse = mouse
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]
        self.calibration_config = utils.get_config('krave.hardware', 'spout_calibration.json')
        self.lick_pin = self.hardware_config['spouts'][spout_name][0]
        self.water_pin = self.hardware_config['spouts'][spout_name][1]

        # calibration info, should be updated everytime calibration is run
        self.calibration_times = self.calibration_config['calibration_times']
        self.total_open_times = self.calibration_config['total_open_times']
        self.water_weights = self.calibration_config['water_weights']
        self.slope = self.calibration_config['slope']

        self.lick_status = 0
        self.lick_record = np.ones([3])
        self.duration = 0
        self.water_opened_time = None
        self.water_dispensing = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lick_pin, GPIO.IN)
        GPIO.setup(self.water_pin, GPIO.OUT)
        GPIO.output(self.water_pin, GPIO.LOW)

    def lick_status_check(self):
        """register change only when current status is different than all three previous status"""
        self.lick_record = np.roll(self.lick_record, 1)
        self.lick_record[0] = GPIO.input(self.lick_pin)
        change_bool = np.all(self.lick_record != self.lick_status)
        change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        self.lick_status += change
        return change

    def water_on(self, reward_size):
        """turns on water, resets duration"""
        GPIO.output(self.water_pin, GPIO.HIGH)
        self.duration = self.calculate_duration(reward_size)
        self.water_dispensing = True
        self.water_opened_time = time.time()

    def water_off(self):
        GPIO.output(self.water_pin, GPIO.LOW)
        self.water_dispensing = False

    def water_cleanup(self):
        if self.water_dispensing and self.water_opened_time + self.duration < time.time():
            self.water_off()

    def shutdown(self):
        self.water_off()
        GPIO.cleanup()
        print("GPIO cleaned up")

    def get_calibration_curve(self):
        """calculates the relationship between solenoid open time and amount of water delivered"""
        self.total_open_times = np.asarray(self.total_open_times).reshape(-1, 1)
        self.water_weights = np.asarray(self.water_weights)
        model = LinearRegression(fit_intercept=False).fit(self.total_open_times, self.water_weights)
        self.slope = model.coef_[0]
        print('slope: ', self.slope)
        print('REMEMBER TO UPDATE TO spout_calibration.json!!!')

    def calibrate(self):
        """
         measure water weights with different open time
        :return: total_open_times and water weights
        """
        self.total_open_times = []
        self.water_weights = []
        try:
            print('calibrating port')
            repeats = 1  # repeating the same weight
            iteration = 100  # number of times opened of solenoid
            for t in self.calibration_times:
                for r in range(repeats):
                    total_open_time = 0
                    for _ in range(iteration):
                        self.water_on(t)
                        time.sleep(t)
                        total_open_time += t
                        self.water_off()
                        time.sleep(0.2)
                    self.total_open_times.append(total_open_time)
                    water_weight = input(f'open time {t} iter {r} water weight: ')
                    self.water_weights.append(float(water_weight))
                    input("Press Enter to continue...")
        finally:
            self.shutdown()
            print(f'total open times {self.total_open_times}')
            print(f'water weights {self.water_weights}')
            self.get_calibration_curve()

    def calculate_duration(self, reward_size_ul):
        """
        calculate how long the solenoid should open based on the size of reward that needs to be delivered
        :param reward_size_ul:
        :return: duration to open spouts
        """
        weight_g = reward_size_ul * 0.001
        self.duration = weight_g / self.slope
        print('sol_open_time: ', round(self.duration, 2))
        return self.duration
