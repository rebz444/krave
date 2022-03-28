import pygame

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption("delay1")

cue_img = pygame.image.load('cheese.png')
cue_x = 150
cue_y = 50
cue_state = "off"


def cue_on(x, y):
    global cue_state
    cue_state = "on"
    screen.blit(cue_img, (x, y))


def cue_off():
    global cue_state
    cue_state = "off"


running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                cue_on(cue_x, cue_y)
                print("Space is pressed")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                cue_off()
                print("Space has been released")

    if cue_state == "on":
        cue_on(cue_x, cue_y)

    pygame.display.update()