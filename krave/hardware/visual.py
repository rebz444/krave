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
        self.cue_duration = self.exp_config['visual_display_duration']
        self.cue_location = tuple(self.exp_config['visual_cue_location'])

        self.cue_displaying = False
        self.cue_on_time = None

        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.cue = pygame.image.load(self.cue_path)
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def cue_on(self):
        self.cue_displaying = True
        self.cue_on_time = time.time()
        self.screen.fill((0, 0, 255))
        # self.screen.blit(self.cue, self.cue_location)
        pygame.display.update()

    def cue_off(self):
        self.cue_displaying = False
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def cue_cleanup(self):
        if self.cue_displaying and self.cue_on_time + self.cue_duration < time.time():
            self.cue_off()
            self.cue_displaying = False

    def shutdown(self):
        self.cue_displaying = False
        pygame.quit()
