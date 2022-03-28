from krave import utils

import pygame


class Visual:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.cue_name = self.exp_config['visual_cue_name']
        self.cue_length = self.exp_config['visual_cue_length']

        self.screen = None
        self.cue = None
        self.cue_displaying = False

    def initialize(self):
        pygame.init()
        pygame.display.set_caption(self.exp_name)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.cue = pygame.image.load(self.cue_name)

    def cue_on(self, x, y):
        self.cue_displaying = True
        self.screen.blit(self.cue, (x, y))

    def cue_off(self):
        self.cue_displaying = False

