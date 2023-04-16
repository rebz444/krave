import time

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.hardware.spout_pump_new import Reward
from krave.output.data_writer import DataWriter

import pygame
import RPi.GPIO as GPIO


class PiTest:
    def __init__(self, exp_name, rig_name):
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{self.exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]

        # self.spout = Spout(self.exp_config, spout_name="1")
        self.visual = Visual(self.exp_config, self.hardware_config)
        self.trigger = Trigger(self.hardware_config)
        self.reward = Reward(self.hardware_config)

        self.start_time = time.time()

    def test_pump_continuous_pulse(self, time_limit=5):
        self.num_pulses = self.reward.calculate_pulses(5)
        while self.start_time + time_limit > time.time():
            self.reward.cleanup()
        self.end()

    def test_pump_single_pulse(self):
        for _ in range(50):
            self.reward.send_single_pulse(self.reward.reward_pin)
        self.end()

    def pump_calibrate(self):
        self.reward.calibrate()
        self.end()

    def free_reward(self):
        num_pulses = self.reward.calculate_pulses(2)
        print(num_pulses)
        for _ in range(10):
            for _ in range(num_pulses):
                self.reward.send_single_pulse(self.reward.reward_pin)
            time.sleep(3)

    def end(self):
        # self.spout.water_off()
        self.visual.shutdown()
        self.trigger.shutdown()
        self.reward.shutdown()

        GPIO.cleanup()

    def test_lick_sensor(self, time_limit=15):
        """prints start and ends lick when spout is touched"""
        start = time.time()
        lick_counter = 0
        while start + time_limit > time.time():
            lick_change = self.reward.lick_status_check()
            if lick_change == 1:
                print(f"start lick {lick_counter} at {time.time() - start:.2f}")
                lick_counter += 1
            elif lick_change == -1:
                print(f"end lick {lick_counter} at {time.time() - start:.2f}")
        self.end()

    def test_visual_cue(self, time_limit=15):
        """flash visual cue when space bar is pressed"""
        start = time.time()
        self.visual.initiate()
        while start + time_limit > time.time():
            self.visual.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('pygame quit')
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.visual.cue_on()
                        print("space is pressed")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.cue_off()
                        print("space is released")
                pygame.display.update()
        self.end()
    #
    # def flush(self, open_time=15):
    #     self.spout.water_on(5)  # the number doesnt do anything
    #     time.sleep(open_time)
    #     self.spout.water_off()
    #     self.end()
    #
    # def free_reward(self, reward_size=5, cool_time=0.02, total_reward=20):
    #     open_time = self.spout.calculate_duration(reward_size)
    #     for _ in range(total_reward):
    #         self.spout.water_on(open_time)
    #         time.sleep(open_time)
    #         self.spout.water_off()
    #         time.sleep(cool_time)
    #     self.end()
    #
    # def lick_validation(self, n_licks=15, time_limit=500):
    #     """mouse licks and water comes out. pictures are taken in the meantime."""
    #     data_writer = DataWriter("test", self.exp_name, self.exp_config, forward_file=False)
    #     lick_counter = 0
    #     lick_display_counter = 0
    #     reward_counter = 0
    #     try:
    #         while self.start_time + time_limit > time.time():
    #             self.trigger.square_wave(data_writer)
    #             self.spout.water_cleanup()
    #             lick_change = self.spout.lick_status_check()
    #             if lick_change == 1:
    #                 lick_counter += 1
    #                 lick_display_counter += 1
    #                 string = f'{reward_counter},{time.time()-self.start_time},{lick_change},lick'
    #                 data_writer.log(string)
    #                 print(f"start lick {lick_display_counter}")
    #             elif lick_change == -1:
    #                 string = f'{reward_counter},{time.time() - self.start_time},{lick_change},lick'
    #                 data_writer.log(string)
    #                 print(f"end lick {lick_display_counter} at {time.time()-self.start_time:.2f} seconds")
    #             if lick_counter >= n_licks:
    #                 lick_counter = 0
    #                 self.spout.water_on(.1)
    #                 reward_counter += 1
    #     finally:
    #         data_writer.end()
    #         self.end()
    #
    # def test_trigger(self, time_limit=200):
    #     """tests square wave"""
    #     data_writer = DataWriter("test", self.exp_name, self.exp_config, forward_file=False)
    #     while self.start_time + time_limit > time.time():
    #         self.trigger.square_wave(data_writer)
    #     self.end()
    #
    # def spout_calibration(self):
    #     self.spout.calibrate()
    #     self.end()
    #
    # def calibration_check(self):
    #     open_time_for_1ul = self.spout.calculate_duration(1)
    #     print(f'open for {open_time_for_1ul}s per 1ul of reward')
    #     self.end()
    #
    # def save_optimal_value_dict(self):
    #     """generate a dict with varying bg_time as keys and [optimal wait time, reward size] as values,
    #     saves the dict as pickle in config folder"""
    #     max_wait_time = self.exp_config['max_wait_time']
    #     wait_time_step_size = self.exp_config['wait_time_step_size']
    #     optimal_value_dict = utils.generate_optimal_value_dict(max_wait_time, wait_time_step_size)
    #     path = 'krave/experiment/config'
    #     filename = self.exp_name + '_optimal_value_dict.pkl'
    #     utils.save_dict_as_pickle(optimal_value_dict, path, filename)
    #     self.end()
    #
    # def test_pump(self):
    #     self.reward.calculate_pulses(4.1)





