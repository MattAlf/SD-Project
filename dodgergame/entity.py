import pygame
from pygame.locals import *
from functions import *
import random

class Entity(pygame.sprite.Sprite):
    def __init__ (self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect() 
        self.rect.topleft = (x, y)

class Player(Entity):
    def __init__(self, x ,y):
        image = settings.PLAYER_IMAGE
        super().__init__(image, x, y)

        self.size = settings.PLAYER_SIZE
        self.image = pygame.transform.scale(image, (self.size, self.size))

        self.speed = settings.PLAYER_MOVE_RATE
        self.vel_y = 0
        self.gravity = settings.PLAYER_GRAVITY
        self.jump_strength = settings.PLAYER_JUMP_STRENGTH 

        self.move_left = False
        self.move_right = False
        self.on_ground = False
        self.on_a_platform = False 

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
        self.vel_y += settings.PLAYER_GRAVITY 
        self.rect.y += self.vel_y

        if self.rect.bottom >= settings.WINDOW_HEIGHT:
            self.rect.bottom = settings.WINDOW_HEIGHT
            self.on_ground = True 
            self.vel_y = 0 
            self.on_a_platform = False 

        for plateform in platform_group:
            if self.vel_y >= 0 and pygame.sprite.collide_rect(self, plateform):
                self.on_ground = True 
                self.vel_y = settings.PLATFORM_SPEED
                self.on_a_platform = True 
                self.rect.bottom = plateform.rect.top 
            else: 
                self.on_a_platform = False 
        
            
        


        # Horizontal movement
        if self.move_left and self.rect.left > 0:
            self.rect.x -= self.speed
        if self.move_right and self.rect.right < settings.WINDOW_WIDTH:
            self.rect.x += self.speed




class Baddies(Entity):
    def __init__ (self, x, y):
        image = settings.BADDIE_IMAGE
        self.size = random.randint(settings.BADDIE_MIN_SIZE, settings.BADDIE_MAX_SIZE)
        x = random.randint(0, settings.WINDOW_WIDTH - self.size)
        y = 0 - self.size
        super().__init__(image, x, y)
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.speed = random.randint(settings.BADDIE_MIN_SPEED, settings.BADDIE_MAX_SPEED)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > settings.WINDOW_HEIGHT:
            self.kill() 

class Platform(Entity):
    def __init__ (self, x , y):
        image = settings.PLATFORM_IMAGE
        self.height = settings.PLATFORM_HEIGHT
        self.width = settings.PLATFORM_WIDTH
        x = random.randint(0, settings.WINDOW_WIDTH - self.width)
        y = random.randint (0, settings.WINDOW_HEIGHT - self.height)
        super().__init__(image, x, y)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self):
        self.rect.y += settings.PLATFORM_SPEED
        if self.rect.top > settings.WINDOW_HEIGHT:
            self.kill()