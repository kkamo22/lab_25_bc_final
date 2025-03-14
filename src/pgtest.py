import math
import sys

import pygame
import pygame.locals


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode(size=(400, 400))

    theta = 0.0

    while True:
        screen.fill(color=(0, 0, 0))

        x = 200 + 50*math.cos(math.radians(theta))
        y = 200 - 50*math.sin(math.radians(theta))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, 10, 10))

        theta += 0.1
        if theta >= 360.0:
            theta = 0.0

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit(0)
