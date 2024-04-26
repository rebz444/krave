import time

from krave.helper.reward_functions import Reward
from krave.helper import utils
from krave.output.data_writer import DataWriter
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.hardware.spout import Spout
from krave.hardware.pi_camera import CameraPi
from krave.hardware.sound import Sound

import pygame
import RPi.GPIO as GPIO


class PiTest:
    def __init__(self, rig_name):
        self.session_config = {"mouse": "test", "exp": "pi_test", "training": " ", "rig": rig_name,
                               "trainer": "Rebekah", "record": False, "forward_file": False}
        self.exp_config = utils.get_config('krave', 'config/exp2_short.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[rig_name]

        # initiate helpers
        self.data_writer = DataWriter(self.session_config, self.exp_config, self.hardware_config)
        self.reward = Reward(self.exp_config)
        self.visual = Visual(self.data_writer)
        self.trigger = Trigger(self.hardware_config, self.data_writer)
        self.spout = Spout(self.hardware_config, self.data_writer)
        self.camera = CameraPi()
        self.sound = Sound()

        self.start_time = time.time()
        self.status = 'nan,nan,nan,nan,nan,'

    def end(self):
        self.visual.shutdown(self.status)
        self.trigger.shutdown()
        self.spout.shutdown()
        self.camera.shutdown()

        GPIO.cleanup()

    def pump_calibrate(self):
        self.spout.calibrate()
        self.end()

    def free_reward(self, reward_size, num_rewards):
        self.camera.on()
        time.sleep(20)
        num_pulses = self.spout.calculate_pulses(reward_size, self.status)
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
            lick_change = self.spout.lick_status_check(self.status)
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
                        self.visual.on(self.status)
                        print("space is pressed")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.off(self.status)
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
                self.trigger.square_wave(self.status)
                self.spout.water_cleanup(self.status)
                lick_change = self.spout.lick_status_check(self.status)
                if lick_change == 1:
                    lick_counter += 1
                    lick_display_counter += 1
                    print(f"start lick {lick_display_counter}")
                elif lick_change == -1:
                    print(f"end lick {lick_display_counter} at {time.time()-self.start_time:.2f} seconds")
                if lick_counter >= n_licks:
                    lick_counter = 0
                    self.spout.calculate_pulses(2, self.status)
                    self.spout.send_continuous_pulse(self.status, self.spout.reward_pin)
                    reward_counter += 1
        finally:
            self.end()

    def test_trigger(self, time_limit=200):
        """tests square wave"""
        while self.start_time + time_limit > time.time():
            self.trigger.square_wave(self.status)
        self.end()





