from krave import utils

import pygame


class PygameVisual:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_name = exp_name
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[hardware_config_name]
        self.cue_name = self.exp_config['visual_cue_name']
        self.cue_path = utils.get_path('krave.hardware', self.cue_name)
        self.cue_length = self.exp_config['visual_cue_length']

        self.screen = None
        self.cue = None
        self.cue_state = "off"

    def initialize(self):
        pygame.init()
        pygame.display.set_caption(self.exp_name)
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.cue = pygame.image.load(self.cue_path)

    def cue_on(self, x, y):
        self.cue_state = "on"
        self.screen.blit(self.cue, (x, y))

    def cue_off(self):
        self.cue_state = "off"
