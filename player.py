# player.py
import pygame
from pygame.locals import *
from functions import *

class Player(pygame.sprite.Sprite):
    def __init__(self, settings, image):
        super().__init__()
        self.settings = settings
        self.size = settings.PLAYER_SIZE

        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.rect = self.image.get_rect(midbottom = (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT))

        self.speed = settings.PLAYER_MOVE_RATE
        self.vel_y = 0
        self.gravity = settings.PLAYER_GRAVITY
        self.jump_strength = settings.PLAYER_JUMP_STRENGTH 

        self.move_left = False
        self.move_right = False
        self.on_ground = False

    def handle_input(self, event):
        if event.type == QUIT:
            terminate()
        
        if event.type == KEYDOWN:
            if event.key in (K_LEFT, K_a):
                self.move_left = True
            if event.key in (K_RIGHT, K_d):
                self.move_right = True
            if event.key in (K_UP, K_w, K_SPACE):
                if self.on_ground:
                    self.vel_y = self.jump_strength
                    self.on_ground = False
        
        if event.type == KEYUP:
            if event.key in (K_LEFT, K_a):
                self.move_left = False
            if event.key in (K_RIGHT, K_d):
                self.move_right = False
            if event.key == K_ESCAPE:
                terminate()

    def update(self, platform_group):
        # Gravity
        if not self.on_ground:
            self.vel_y += self.gravity

        # Vertical movement
        self.rect.y += self.vel_y

        # Reset ground state before collision checks
        self.on_ground = False
        # PLATFORM collision using sprite collision
        self.check_platform_collisions(platform_group)
        self.check_ground_collision()

        # Horizontal movement
        if self.move_left and self.rect.left > 0:
            self.rect.x -= self.speed
        if self.move_right and self.rect.right < self.settings.WINDOW_WIDTH:
            self.rect.x += self.speed

    def check_platform_collisions(self, platform_group):
        hits = pygame.sprite.spritecollide(self, platform_group, False)
        for p in hits:
            if self.rect.colliderect(p.rect):

                # Only collide when falling
                if self.vel_y >= 0 and self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def check_ground_collision(self):
        if self.rect.bottom >= self.settings.WINDOW_HEIGHT:
            self.rect.bottom = self.settings.WINDOW_HEIGHT
            self.vel_y = 0
            self.on_ground = True
