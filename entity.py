import pygame
from pygame.locals import *
from functions import *
from settings import *
import random

class Entity(pygame.sprite.Sprite):
    def __init__ (self, image, image_width, image_height):
        super().__init__()
        self.image = pygame.transform.scale(image, (image_width, image_height))
        self.rect = self.image.get_rect()

class Player(Entity):
    def __init__(self):
        image = settings.PLAYER_IMAGE
        self.size = settings.PLAYER_SIZE
        super().__init__(image, self.size, self.size)
        self.rect.midbottom = (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - settings.PLATFORM_HEIGHT)

        # Stores the 2D vector (so it's more convinient to use)
        self.vector = pygame.math.Vector2
        # Kinematic vectors (x,y)
        self.position = self.vector(self.rect.left, self.rect.bottom)
        self.velocity = self.vector(0, 0)
        self.acceleration = self.vector(0, 0)
        # Kinematic constants
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGTH = settings.PLAYER_JUMP_STRENGTH

        self.move_left = False
        self.move_right = False

    def handle_input(self, ground_group, platform_group):
        for event in pygame.event.get():
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
        # Check for the player's input at each update
        self.handle_input(ground_group, platform_group)

        # Set the initial acceleration to (0, gravity)
        self.acceleration = self.vector(0, self.VERTICAL_ACCELERATION)

        # Update the horizontal acceleration of the player according to the inputs
        if self.move_left:
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
        if self.move_right:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION

        # Calculate the new kinematics
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Make the player stay within the window screen
        self.check_for_screen_border_collision()

        # Update the player's rectangle position
        self.rect.bottomleft = self.position

        # Check for collisions with the ground and the platforms. We have to put it after we
        # update the player's rectangle so that the jumping mechanics work.
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
        if self.position.x + self.size >= settings.WINDOW_WIDTH:
            self.position.x = settings.WINDOW_WIDTH - self.size

    # We only allow the player to jump when he collides a platform or the ground.
    # But we have to specify that the jumps is enabled only when the player is over the object.
    # (The collision between the bottom of the player and the top of the object)
    def player_jump(self, ground_group, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)

        # The player needs to collide with the object and the player's bottom needs to be at least
        # half the object's height over the objeect (to avoid jumping bugs).
        if touched_ground and self.rect.bottom <= touched_ground[0].rect.top + settings.GROUND_HEIGHT // 2:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH
        if touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + settings.PLATFORM_HEIGHT // 2:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH

class Baddies(Entity):
    def __init__ (self):
        image = settings.BADDIE_IMAGE
        self.size = random.randint(settings.BADDIE_MIN_SIZE, settings.BADDIE_MAX_SIZE)
        super().__init__(image, self.size, self.size)

        # Set the Baddie's position randomly
        self.rect.left = random.randint(0, settings.WINDOW_WIDTH - self.size)
        self.rect.bottom = 0

        # Set the Baddie's speed randomly
        self.speed = random.randint(settings.BADDIE_MIN_SPEED, settings.BADDIE_MAX_SPEED)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > settings.WINDOW_HEIGHT:
            self.kill()

class Platform(Entity):
    def __init__ (self):
        image = settings.PLATFORM_IMAGE
        self.height = settings.PLATFORM_HEIGHT
        self.width = settings.PLATFORM_WIDTH
        super().__init__(image, self.width, self.height)

        self.rect.left = random.randint(0, settings.WINDOW_WIDTH - self.width)
        self.rect.top = random.randint(0, settings.WINDOW_HEIGHT - self.height)

    def update(self):
        if self.rect.top > settings.WINDOW_HEIGHT:
            self.kill()

class Ground(Entity):
    def __init__(self):
        image = settings.GROUND_IMAGE
        self.width = settings.WINDOW_WIDTH
        self.height = settings.GROUND_HEIGHT
        super().__init__(image, self.width, self.height)

        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT)

class Background(Entity):
    def __init__(self, x, y):
        image = settings.BACKGROUND_IMAGE
        self.width = settings.WINDOW_WIDTH
        self.height = settings.WINDOW_HEIGHT
        super().__init__(image, self.width, self.height)

        self.rect.topleft = (x, y)
        
        # The scroll speed should match the BG_SCROLL_SPEED setting
        self.speed = settings.BACKGROUND_SCROLL_SPEED

    def update(self):
        # Move the background image down
        self.rect.y += self.speed
        
        # If the image has scrolled entirely off the bottom of the screen,
        # reset its position to be directly above the screen (for seamless looping).
        if self.rect.top >= settings.WINDOW_HEIGHT:
            self.rect.top = -settings.WINDOW_HEIGHT