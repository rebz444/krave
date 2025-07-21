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
        display_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.NOFRAME )
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

    def test_visual_cue(self, time_limit=5):
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
                        self.visual.on(self.status)
                        print("space is pressed")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.visual.off(self.status)
                        print("space is released")
                pygame.display.update()
        self.end()

if __name__ == "__main__":
    visual = Visual()
    visual.test_visual_cue()



