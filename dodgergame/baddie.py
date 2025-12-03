# baddie.py
import pygame
import random
from pygame.locals import *

class Baddie(pygame.sprite.Sprite):
    def __init__(self, settings, image):
        super().__init__()
        self.settings = settings
        self.size = random.randint(settings.BADDIE_MIN_SIZE, settings.BADDIE_MAX_SIZE)
        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.rect = self.image.get_rect(midbottom = (random.randint(0, settings.WINDOW_WIDTH - self.size), 0))
        self.speed = random.randint(settings.BADDIE_MIN_SPEED, settings.BADDIE_MAX_SPEED)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > self.settings.WINDOW_HEIGHT:
            self.kill()    
