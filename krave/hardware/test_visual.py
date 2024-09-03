import os
import pygame
import time

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,600)

pygame.init()

screen = pygame.display.set_mode((1024, 600), pygame.NOFRAME )
screen.fill((0, 0, 255))

pygame.display.update()

time.sleep(5)

pygame.quit()

