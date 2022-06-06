import time

from krave import utils

import pygame


class Visual:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.cue_name = self.exp_config['visual_cue_name']
        self.cue_path = utils.get_path('krave.hardware', f'visual_cue_img/{self.cue_name}')
        self.cue_length = self.exp_config['visual_cue_length']

        self.screen = None
        self.cue = None
        self.screen_ready = False
        self.cue_displaying = False

    def initialize(self):
        pygame.init()
        pygame.display.set_caption(self.exp_name)
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.screen_ready = True
        self.cue = pygame.image.load(self.cue_path)
        return time.time()

    def cue_on(self, x, y):
        self.cue_displaying = True
        self.screen.blit(self.cue, (x, y))
        return time.time()

    def cue_off(self):
        self.cue_displaying = False
        return time.time()

    def shutdown(self):
        pygame.quit()
        self.screen_ready = False
        return time.time()
