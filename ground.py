# ground.py
import pygame

class Ground(pygame.sprite.Sprite):
    def __init__(self, settings, image):
        super().__init__()
        self.settings = settings
        self.image = pygame.transform.scale(image, (settings.WINDOW_WIDTH, 10))
        self.rect = self.image.get_rect(bottomleft = (0, settings.WINDOW_HEIGHT))
