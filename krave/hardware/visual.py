import time
import os

import pygame


class Visual:
    def __init__(self, data_writer):
        self.data_writer = data_writer
        self.cue_displaying = False
        self.cue_on_time = None
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,600'

        pygame.init()
        self.screen = pygame.display.set_mode((1024, 600))
        # self.screen = pygame.display.set_mode((720, 480))  # for running when on desktop

        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def cue_on(self):
        """can flash the screen or show an image. currently flashing the screen green."""
        self.screen.fill((0, 255, 0))
        pygame.display.update()

        self.cue_displaying = True
        self.cue_on_time = time.time()
        self.data_writer.log('nan,nan,nan,nan,nan,nan,1,visual')

    def cue_off(self):
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        self.cue_displaying = False
        self.data_writer.log('nan,nan,nan,nan,nan,nan,0,visual')

    def shutdown(self):
        self.cue_displaying = False
        pygame.quit()
