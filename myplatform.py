# platform.py
import pygame
import random
from pygame.locals import *

class MyPlatform(pygame.sprite.Sprite):
    def __init__(self, settings, score, image):
        super().__init__()
        if score < 1000:
            self.width = 100
        elif score < 2000:
            self.width = 80
        elif score < 3000:
            self.width = 60
        else:
            self.width = 40
        self.height = settings.PLATFORM_HEIGHT
        self.image = pygame.transform.scale(image, (self.width, self.height))

        self.rect = self.image.get_rect(topleft = ((random.randint(0, settings.WINDOW_WIDTH - self.width)), 550 - self.height))
