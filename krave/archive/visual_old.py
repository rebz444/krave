import time

import pygame


class Visual:
    """
    old version of visual cue displaying.
    includes code to display an image, and displaying cue for a set amount of time
    """
    def __init__(self, exp_config):
        self.cue_duration = exp_config['visual_cue_duration']

        self.cue_displaying = False
        self.cue_on_time = None
        self.screen = None

        # used for displaying an image (currently not in use)
        # self.cue_name = self.exp_config['visual_cue_name']
        # self.cue_path = utils.get_path('krave.hardware', f'visual_cue_img/{self.cue_name}')
        # self.cue_location = tuple(self.exp_config['visual_cue_location'])
        # self.cue = pygame.image.load(self.cue_path)

    def initiate(self):
        pygame.init()
        # self.screen = pygame.display.set_mode((1024, 600))
        size = (720, 480)
        self.screen = pygame.display.set_mode(size)

        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def cue_on(self):
        """can flash the screen or show an image. currently flashing the screen green."""
        self.cue_displaying = True
        self.cue_on_time = time.time()
        self.screen.fill((0, 255, 0))
        # self.screen.blit(self.cue, self.cue_location)
        pygame.display.update()

    def cue_off(self):
        self.cue_displaying = False
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def cleanup(self):
        if self.cue_displaying and self.cue_on_time + self.cue_duration < time.time():
            self.cue_off()

    def shutdown(self):
        self.cue_displaying = False
        pygame.quit()