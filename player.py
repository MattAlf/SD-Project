# player.py
import pygame
from pygame.locals import *
from functions import *

class Player(pygame.sprite.Sprite):
    def __init__(self, settings, image):
        super().__init__()
        self.settings = settings
        self.player_size = settings.PLAYER_SIZE

        self.image = pygame.transform.scale(image, (self.player_size, self.player_size))
        self.rect = self.image.get_rect(midbottom = (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT))

        # stores the 2D vector (so it's more convinient to use)
        self.vector = pygame.math.Vector2
        # Kinematic vectors (x,y)
        self.position = self.vector(self.rect.x, self.rect.y)
        self.velocity = self.vector(0,0)
        self.acceleration = self.vector(0,0)
        # Kinematic constants
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGHT = settings.PLAYER_JUMP_STRENGTH

        self.move_left = False
        self.move_right = False

    def handle_input(self, event, ground_group, platform_group):
        if event.type == QUIT:
            terminate()
        
        if event.type == KEYDOWN:
            if event.key in (K_LEFT, K_a):
                self.move_left = True
            if event.key in (K_RIGHT, K_d):
                self.move_right = True
            if event.key in (K_UP, K_w, K_SPACE):
                self.player_jump(ground_group, platform_group)
        
        if event.type == KEYUP:
            if event.key in (K_LEFT, K_a):
                self.move_left = False
            if event.key in (K_RIGHT, K_d):
                self.move_right = False
            if event.key == K_ESCAPE:
                terminate()

    def update(self, ground_group, platform_group):
        for event in pygame.event.get():
            self.handle_input(event, ground_group, platform_group)
        # Set the initial acceleration to (0,0)
        self.acceleration = self.vector(0,self.VERTICAL_ACCELERATION)

        if self.move_left:
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
        if self.move_right:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION

        # Calculate the new kinematics
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Makes the player stay within the window screen
        self.check_for_screen_border_collision()

        # Update the player rectangle
        self.rect.bottomleft = self.position

        # Check for collisions with ground. We have to put it after we update the player rectangle
        # so that the jumping mechanics work.
        self.check_platform_collisions(platform_group)
        self.check_ground_collision(ground_group)

    def check_platform_collisions(self, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        if touched_platforms:
            if self.velocity.y > 0 and self.rect.bottom < touched_platforms[0].rect.bottom:
                self.position.y = touched_platforms[0].rect.top
                self.velocity.y = 0

    def check_ground_collision(self, ground_group):
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground:
            self.position.y = touched_ground[0].rect.top
            self.velocity.y = 0

    def check_for_screen_border_collision(self):
        if self.position.x <= 0:
            self.position.x = 0
        if self.position.x + self.player_size >= settings.WINDOW_WIDTH:
            self.position.x = settings.WINDOW_WIDTH - self.player_size

    def player_jump(self, ground_group, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground and self.rect.bottom <= touched_ground[0].rect.top + 1:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGHT
        if touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + 1:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGHT