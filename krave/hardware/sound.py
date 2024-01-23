import time

import pygame.mixer

from krave.helper import utils


class Sound:
    def __init__(self):
        pygame.mixer.init()
        self.sound_path = utils.get_path('krave.hardware', 'end_tone.wav')
        self.tone = pygame.mixer.Sound(self.sound_path)

    def on(self):
        pygame.mixer.Sound.play(self.tone)
        time.sleep(5)


if __name__ == '__main__':
    Sound().on()
