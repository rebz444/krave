import time

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.camera_trigger import CameraTrigger
from krave.output.data_writer import DataWriter

import RPi.GPIO as GPIO
import pygame


def reward_function(t):
    return .1


class PiTest:
    def __init__(self, mouse, exp_name):
        self.mouse = mouse
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        self.cue_duration = self.exp_config["visual_display_duration"]

        self.spout = Spout(self.mouse, self.exp_config, spout_name="1")
        self.visual = Visual(self.mouse, self.exp_config)
        self.data_writer = DataWriter(self.mouse, self.exp_name, self.exp_config)
        self.camera_trigger = CameraTrigger(self.mouse, self.exp_config)

        self.running = False

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def test_lick(self):
        try:
            time_limit = 60
            start = time.time()
            lick_counter = 0
            while start + time_limit > time.time():
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    print(f"start lick {lick_counter}")
                    lick_counter += 1
                elif lick_change == -1:
                    print(f"end lick {lick_counter} at {time.time()}")
        finally:
            self.spout.shutdown()

    def test_visual_cue(self):
        self.visual.initialize()
        start = time.time()
        time_limit = 20
        while start + time_limit > time.time():
            self.running = True
            while self.running:
                self.visual.screen.fill((0, 0, 0))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.visual.cue_on()
                            print("space is pressed")
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            self.visual.cue_off()
                            print("space is released")
                # if self.visual.cue_displaying:
                #     self.visual.cue_on()
                pygame.display.update()
        self.visual.shutdown()

    def test_water(self, iterations, open_time, cool_time):
        try:
            for i in range(iterations):
                self.spout.water_on(.01)
                time.sleep(open_time)
                print('drop delivered')
                self.spout.water_off()
                time.sleep(cool_time)
        finally:
            self.spout.shutdown()
            self.running = False

    def test_visual_with_lick(self):
        self.visual.initialize()
        time_limit = 30
        start = time.time()
        lick_counter = 0
        try:
            while start + time_limit > time.time():
                self.running = True
                self.visual.screen.fill((0, 0, 0))
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    print(f"start lick {lick_counter}")
                    self.visual.cue_on()
                    self.spout.water_on(.01)
                elif lick_change == -1:
                    self.visual.cue_off()
                    print(f"end lick {lick_counter} at {time.time()}")
                    lick_counter += 1
                    self.spout.water_off()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                if self.visual.cue_displaying:
                    self.visual.cue_on()
                pygame.display.update()
        finally:
            GPIO.cleanup()
            print("GPIO cleaned up")
            self.visual.shutdown()

    def lick_validation(self, n_licks, time_limit=500):
        start_time = time.time()
        lick_counter = 0
        lick_display_counter = 0
        reward_counter = 0
        try:
            while start_time + time_limit > time.time():
                self.camera_trigger.square_wave(self.data_writer)
                self.spout.water_cleanup()
                self.running = True
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    lick_display_counter += 1
                    string = f'{reward_counter},{time.time()-start_time},{lick_change},lick'
                    self.data_writer.log(string)
                    print(f"start lick {lick_display_counter}")
                elif lick_change == -1:
                    string = f'{reward_counter},{time.time() - start_time},{lick_change},lick'
                    self.data_writer.log(string)
                    print(f"end lick {lick_display_counter} at {time.time()-start_time:.2f} seconds")
                if lick_counter >= n_licks:
                    lick_counter = 0
                    self.spout.water_on(.1)
                    reward_counter += 1
        finally:
            self.spout.shutdown()
            self.data_writer.end(forward=True)  # sends file to pc and deletes from pi
            self.running = False

    def reset(self):
        self.spout.shutdown()

    def spout_calibration(self):
        self.spout.calibrate()
        self.spout.calculate_duration(2.7)



