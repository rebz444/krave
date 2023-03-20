import time
import json
import os

from krave import utils

import RPi.GPIO as GPIO
import numpy as np
from sklearn.linear_model import LinearRegression


class Spout:
    def __init__(self, exp_config, spout_name):
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]
        self.lick_pin = self.hardware_config['spouts'][spout_name][0]
        self.water_pin = self.hardware_config['spouts'][spout_name][1]
        self.calibration_times = self.hardware_config['spout_calibration_times']

        # calibration info, loads the latest calibration file from pi
        self.calibration_file_path = os.path.join('/home', 'pi', 'Documents', 'spout_calibration')
        # calibration_latest_file = utils.get_latest_filename(self.calibration_file_path, '*.json')
        # print(f"last calibration date is {calibration_latest_file}")
        # with open(calibration_latest_file) as f:
        #     self.calibration_config = json.load(f)
        # activate the line below if no previous calibration info has been saved on the pi
        self.calibration_config = utils.get_config('krave.hardware', 'spout_calibration.json')
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

    def get_calibration_curve(self):
        """calculates the relationship between solenoid open time and amount of water delivered"""
        self.total_open_times = np.asarray(self.total_open_times).reshape(-1, 1)
        self.water_weights = np.asarray(self.water_weights)
        model = LinearRegression(fit_intercept=False).fit(self.total_open_times, self.water_weights)
        self.slope = model.coef_[0]
        print('slope: ', self.slope)

    def save_calibration_json(self):
        calibration_dict = {
            "calibration_times": self.calibration_times,
            "total_open_times": self.total_open_times.flatten().tolist(),
            "water_weights": self.water_weights.tolist(),
            "slope": self.slope
        }
        datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        json_name = "calibration_" + datetime + ".json"
        utils.save_dict_as_json(calibration_dict, self.calibration_file_path, json_name)

    def calibrate(self, repeats=1):
        """
         measure water weights with different open time
        :return: total_open_times and water weights
        """
        self.total_open_times = []
        self.water_weights = []
        tube_weights = []
        print(f"{len(self.calibration_times) * repeats} tubes needed for calibration")
        iteration = 100  # number of times opened of solenoid
        try:
            for n in range(len(self.calibration_times) * repeats):
                tube_weights.append(float(input(f'tube {n} weight: ')))

            n = 0
            for t in self.calibration_times:
                for r in range(repeats):
                    total_open_time = 0
                    input(f"get tube {n} ready, press Enter to start dispensing water ..")
                    n += 1
                    for _ in range(iteration):
                        GPIO.output(self.water_pin, GPIO.HIGH)
                        time.sleep(t)
                        total_open_time += t
                        GPIO.output(self.water_pin, GPIO.LOW)
                        time.sleep(0.2)
                    self.total_open_times.append(total_open_time)

            input("measure tube weights, press Enter to entering values ..")
            for n in range(len(self.calibration_times) * repeats):
                water_tube_weight = float(input(f'tube {n} with water weight: '))
                self.water_weights.append(water_tube_weight - tube_weights[n])
        finally:
            self.water_off()
            print(f'total open times {self.total_open_times}')
            print(f'water weights {self.water_weights}')
            self.get_calibration_curve()
            self.save_calibration_json()
            open_time_for_1ul = self.calculate_duration(1)
            print(f'open for {open_time_for_1ul:.3f}s per 1ul of reward')

    def calculate_duration(self, reward_size_ul):
        """
        calculate how long the solenoid should open based on the size of reward that needs to be delivered
        :param reward_size_ul:
        :return: duration to open spouts
        """
        weight_g = reward_size_ul * 0.001
        self.duration = weight_g / self.slope
        return self.duration
