import time

from krave import utils

import pygame


class Visual:
    def __init__(self, mouse, exp_config):
        self.mouse = mouse
        self.exp_config = exp_config
        self.hardware_config_name = self.exp_config['hardware_setup']
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[self.hardware_config_name]

        self.cue_name = self.exp_config['visual_cue_name']
        self.cue_path = utils.get_path('krave.hardware', f'visual_cue_img/{self.cue_name}')
        self.cue_length = self.exp_config['visual_cue_length']

        self.screen = None
        self.cue = None
        self.cue_displaying = False

        pygame.init()
        self.screen_ready = True
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.cue = pygame.image.load(self.cue_path)

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
