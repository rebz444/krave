import time

from krave import utils
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.hardware.spout import Spout
from krave.hardware.pi_camera import CameraPi
from krave.output.data_writer import DataWriter

import pygame
import RPi.GPIO as GPIO


class PiTest:
    def __init__(self, exp_name, rig_name):
        self.exp_config = utils.get_config('krave', f'config/{exp_name}.json')
        hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]

        self.data_writer = DataWriter("test", exp_name, "hardware_test", rig_name, hardware_config, forward_file=False)
        self.visual = Visual(self.data_writer)
        self.trigger = Trigger(hardware_config, self.data_writer)
        self.spout = Spout(hardware_config, self.data_writer)
        self.camera = CameraPi()

        self.start_time = time.time()

    def end(self):
        self.visual.shutdown()
        self.trigger.shutdown()
        self.spout.shutdown()
        self.camera.shutdown()

        GPIO.cleanup()

    def pump_calibrate(self):
        print(self.spout.interval)
        self.spout.calibrate()
        self.end()

    def free_reward(self, reward_size, num_rewards):
        self.camera.on()
        time.sleep(20)
        num_pulses = self.spout.calculate_pulses(reward_size)
        print(num_pulses)
        for i in range(num_rewards):
            print(f'reward number {i}')
            for _ in range(num_pulses):
                self.spout.send_single_pulse(self.spout.reward_pin)
            time.sleep(3)
        self.end()

    def test_pi_camera_preview(self):
        self.camera.on()
        time.sleep(20)
        self.camera.shutdown()
        self.end()

    def test_lick_sensor(self, time_limit=40):
        """prints start and ends lick when spout is touched"""
        start = time.time()
        lick_counter = 0
        while start + time_limit > time.time():
            lick_change = self.spout.lick_status_check()
            if lick_change == 1:
                print(f"start lick {lick_counter} at {time.time() - start:.2f}")
                lick_counter += 1
            elif lick_change == -1:
                print(f"end lick {lick_counter} at {time.time() - start:.2f}")
        self.end()

    def test_visual_cue(self, time_limit=15):
        """flash visual cue when space bar is pressed"""
        start = time.time()
        while start + time_limit > time.time():
            self.visual.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('pygame quit')
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.visual.on()
                        print("space is pressed")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.off()
                        print("space is released")
                pygame.display.update()
        self.end()

    def lick_validation(self, n_licks=15, time_limit=500):
        """mouse licks and water comes out. pictures are taken in the meantime."""
        lick_counter = 0
        lick_display_counter = 0
        reward_counter = 0
        try:
            while self.start_time + time_limit > time.time():
                self.trigger.square_wave()
                self.spout.water_cleanup()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    lick_display_counter += 1
                    print(f"start lick {lick_display_counter}")
                elif lick_change == -1:
                    print(f"end lick {lick_display_counter} at {time.time()-self.start_time:.2f} seconds")
                if lick_counter >= n_licks:
                    lick_counter = 0
                    self.spout.calculate_pulses(2)
                    self.spout.send_continuous_pulse(self.spout.reward_pin)
                    reward_counter += 1
        finally:
            self.end()

    def test_trigger(self, time_limit=200):
        """tests square wave"""
        while self.start_time + time_limit > time.time():
            self.trigger.square_wave()
        self.end()

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





