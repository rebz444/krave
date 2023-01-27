import time

from krave import utils
from krave.hardware.spout import Spout
from krave.hardware.visual import Visual
from krave.hardware.trigger import Trigger
from krave.output.data_writer import DataWriter

import pygame
import RPi.GPIO as GPIO


class PiTest:
    def __init__(self, exp_name):
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{self.exp_name}.json')
        self.hardware_name = self.exp_config['hardware_setup']

        self.spout = Spout(self.exp_config, spout_name="1")
        self.visual = Visual(self.exp_config)
        self.trigger = Trigger(self.exp_config)

    def end(self):
        self.visual.shutdown()
        self.spout.water_off()
        self.trigger.shutdown()

        GPIO.cleanup()

    def test_lick_sensor(self, time_limit=15):
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
                        self.visual.cue_on()
                        print("space is pressed")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.cue_off()
                        print("space is released")
                pygame.display.update()
        self.end()

    def test_water(self, open_time=0.01, cool_time=0.2, iterations=1000):
        """opens solenoid repeatedly"""
        for i in range(iterations):
            self.spout.water_on(5)
            time.sleep(open_time)
            print('drop delivered')
            self.spout.water_off()
            time.sleep(cool_time)
        self.end()

    def lick_validation(self, n_licks=15, time_limit=500):
        """mouse licks and water comes out. pictures are taken in the meantime."""
        data_writer = DataWriter("test", self.exp_name, self.exp_config, forward_file=False)
        start_time = time.time()
        lick_counter = 0
        lick_display_counter = 0
        reward_counter = 0
        try:
            while start_time + time_limit > time.time():
                self.trigger.square_wave(data_writer)
                self.spout.water_cleanup()
                lick_change = self.spout.lick_status_check()
                if lick_change == 1:
                    lick_counter += 1
                    lick_display_counter += 1
                    string = f'{reward_counter},{time.time()-start_time},{lick_change},lick'
                    data_writer.log(string)
                    print(f"start lick {lick_display_counter}")
                elif lick_change == -1:
                    string = f'{reward_counter},{time.time() - start_time},{lick_change},lick'
                    data_writer.log(string)
                    print(f"end lick {lick_display_counter} at {time.time()-start_time:.2f} seconds")
                if lick_counter >= n_licks:
                    lick_counter = 0
                    self.spout.water_on(.1)
                    reward_counter += 1
        finally:
            data_writer.end()
            self.end()

    def test_trigger(self, time_limit=200):
        """tests square wave"""
        data_writer = DataWriter("test", self.exp_name, self.exp_config, forward_file=False)
        start_time = time.time()
        while start_time + time_limit > time.time():
            self.trigger.square_wave(data_writer)
        self.end()

    def test_calibration(self):
        """test water calibration function"""
        self.spout.calibrate()
        self.end()


