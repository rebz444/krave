import time

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.pygame_visual import Visual
from krave.output.data_writer import DataWriter

import RPi.GPIO as GPIO
import pygame


class PiTest:
    def __init__(self, info):
        self.info = info
        self.mouse = info.mouse
        self.exp_name = info.exp_name
        self.exp_config = self.get_config()
        self.hardware_name = self.exp_config['hardware_setup']
        self.spout = Spout(self.exp_name, self.hardware_name, "1", 0.3)
        self.visual = Visual(self.exp_name, self.hardware_name)
        self.data_writer = DataWriter(self.info)

        self.running = False

    def get_config(self):
        """Get experiment config from json"""
        return utils.get_config('krave.experiment', f'config/{self.exp_name}.json')

    def test_lick(self):
        self.spout.initialize()
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
            self.visual.screen.fill((0, 0, 0))
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

            if self.visual.cue_displaying:
                self.visual.cue_on(x, y)

            pygame.display.update()

    def test_water(self):
        self.spout.initialize()
        try:
            for i in range(20):
                self.spout.water_on()
                time.sleep(.1)
                print('drop delivered')
                self.spout.water_off()
                time.sleep(.5)
        finally:
            self.spout.shutdown()
            self.running = False

    def test_visual_with_lick(self, x, y):
        self.spout.initialize()
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
                    self.visual.cue_on(x, y)
                    self.spout.water_on()
                elif lick_change == -1:
                    self.visual.cue_off()
                    print(f"end lick {lick_counter} at {time.time()}")
                    lick_counter += 1
                    self.spout.water_off()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                if self.visual.cue_displaying:
                    self.visual.cue_on(x, y)

                pygame.display.update()
        finally:
            GPIO.cleanup()
            print("GPIO cleaned up")
            self.visual.shutdown()

    def test_lick_with_mouse(self, n_licks, time_limit=300):
        self.spout.initialize()
        start = time.time()
        lick_counter = 0
        lick_display_counter = 0
        try:
            while start + time_limit > time.time():
                self.spout.water_cleanup()
                self.running = True
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    lick_display_counter += 1
                    print(f"start lick {lick_display_counter}")
                elif lick_change == -1:
                    print(f"end lick {lick_display_counter} at {time.time()-start:.2f} seconds")
                if lick_counter >= n_licks:
                    lick_counter = 0
                    self.spout.water_on()
        finally:
            self.spout.shutdown()
            self.running = False

    def test_data_writer(self):
        self.data_writer.start()

