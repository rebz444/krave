import time
import os

from krave.hardware.spout import Spout
from krave.hardware.pygame_visual import PygameVisual
from krave import utils

import RPi.GPIO as GPIO
import pygame


class PiTest:
    def __init__(self, exp_name):
        self.exp_name = exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        self.spout = Spout(self.exp_name, self.hardware_name, "1")
        self.visual = PygameVisual(self.exp_name, self.hardware_name)

        self.running = True

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def test_spout(self):
        self.spout.initialize_spout()
        try:
            time_limit = 60
            start = time.time()
            lick_counter = 0
            while start + time_limit > time.time():
                # self.spout.test_spout()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    print(f"start lick {lick_counter}")
                    lick_counter += 1
                elif lick_change == -1:
                    print(f"end lick {lick_counter} at {time.time()}")
        finally:
            GPIO.cleanup()

    def test_visual_cue(self, x, y):
        self.visual.initialize()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.visual.cue_on(x, y)
                        print("space is pressed")

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.cue_off()
                        print("space is released")

            if self.visual.cue_state == "on":
                self.visual.cue_on(x, y)

            pygame.display.update()



