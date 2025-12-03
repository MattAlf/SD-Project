# background.py
import pygame

class Background(pygame.sprite.Sprite):
    def __init__(self, settings, image, y_position):
        super().__init__()
        self.settings = settings
        
        # Scale the image to perfectly fit the screen width and height
        self.image = pygame.transform.scale(image, (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        
        # Set the rect, using the provided initial Y position
        self.rect = self.image.get_rect(topleft = (0, y_position))
        
        # The scroll speed should match the BG_SCROLL_SPEED setting
        self.speed = settings.BACKGROUND_SCROLL_SPEED

    def update(self):
        # Move the background image down
        self.rect.y += self.speed
        
        # If the image has scrolled entirely off the bottom of the screen,
        # reset its position to be directly above the screen (for seamless looping).
        if self.rect.top >= self.settings.WINDOW_HEIGHT:
            self.rect.y = -self.settings.WINDOW_HEIGHT