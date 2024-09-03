import time
import os

import pygame


class Visual:
    def __init__(self, data_writer):
        self.data_writer = data_writer
        self.cue_displaying = False
        self.cue_on_time = None

        # pygame.init()
        self.screen = pygame.display.set_mode((1024, 600), pygame.NOFRAME )
        self.screen.fill((0, 0, 255))

        pygame.display.update()

    def on(self, status):
        """can flash the screen or show an image. currently flashing the screen green."""
        self.screen.fill((0, 255, 0))
        pygame.display.update()

        self.cue_displaying = True
        self.cue_on_time = time.time()
        self.data_writer.log(status + 'nan,1,visual')

    def off(self, status):
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        self.cue_displaying = False
        self.data_writer.log(status + 'nan,0,visual')

    def shutdown(self, status):
        if self.cue_displaying:
            self.off(status)
        self.cue_displaying = False
        pygame.quit()




