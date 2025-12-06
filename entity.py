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

class Player(pygame.sprite.Sprite):
    def __init__(self, PLAYER_IMAGES):
        super().__init__()
        self.current_image_index = 0
        self.player_images = PLAYER_IMAGES

        target_height = settings.PLAYER_HEIGHT

        original_image = self.player_images['PLAYER_IDLE_RIGHT'][0]
        original_width = original_image.get_width()
        original_height = original_image.get_height()

        scale_factor = target_height / original_height
        self.draw_height = target_height
        self.draw_width = int(original_width * scale_factor)

        self.image = pygame.transform.scale(original_image, (self.draw_width, self.draw_height))

        hitbox_width = int(self.draw_width * 0.17)  
        hitbox_height = int(self.draw_height * 0.50)

        self.HITBOX_X_OFFSET = int(self.draw_width * 0.42)
        self.HITBOX_Y_OFFSET = int(self.draw_height * 0.33)

        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)

        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT - settings.PLATFORM_HEIGHT)

        self.full_image_rect = self.image.get_rect()
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)

        # Kinematic vectors (x,y)
        self.position = pygame.math.Vector2(self.rect.left, self.rect.bottom)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        # Kinematic constants
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGTH = settings.PLAYER_JUMP_STRENGTH
        
        self.run_left = False
        self.run_right = False
        self.in_a_jump = False
        self.on_ground = True
        self.on_platform = False

    def handle_input(self, ground_group, platform_group):
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            
            if event.type == KEYDOWN:
                if event.key in (K_LEFT, K_a):
                    self.run_left = True
                if event.key in (K_RIGHT, K_d):
                    self.run_right = True
                if event.key in (K_UP, K_w, K_SPACE) and (self.on_ground or self.on_platform):
                    self.player_jump(ground_group, platform_group)
                    self.on_ground = False
                    self.on_platform = False
                    self.in_a_jump = True
            
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a):
                    self.run_left = False
                    self.current_image_index = 0
                if event.key in (K_RIGHT, K_d):
                    self.run_right = False
                    self.current_image_index = 0
                if event.key == K_ESCAPE:
                    terminate()

    def update(self, ground_group, platform_group):
        # Check for the player's input at each update
        self.handle_input(ground_group, platform_group)

        # Set the initial acceleration to (0, gravity)
        self.acceleration = pygame.math.Vector2(0, self.VERTICAL_ACCELERATION)

        # Update the horizontal acceleration of the player according to the inputs
        
        if self.in_a_jump and not self.on_ground and not self.on_platform:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_JUMP_RIGHT'], settings.PLAYER_ANIMATION_SPEED)
                print('JUMPRIGHT')
            else:
                self.animate(self.player_images['PLAYER_JUMP_LEFT'], settings.PLAYER_ANIMATION_SPEED)
                print('JUMPLEFT')
        elif self.run_left or self.run_right:
            if self.run_left:
                self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
                self.animate(self.player_images['PLAYER_RUN_LEFT'], settings.PLAYER_ANIMATION_SPEED)
            if self.run_right:
                self.acceleration.x = self.HORIZONTAL_ACCELERATION
                self.animate(self.player_images['PLAYER_RUN_RIGHT'], settings.PLAYER_ANIMATION_SPEED)
        else:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_IDLE_RIGHT'], settings.PLAYER_ANIMATION_SPEED)
            else:
                self.animate(self.player_images['PLAYER_IDLE_LEFT'], settings.PLAYER_ANIMATION_SPEED)

        # Calculate the new kinematics
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Make the player stay within the window screen
        self.check_for_screen_border_collision()

        # Update the player's rectangle position
        self.rect.bottomleft = self.position
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)

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
                self.on_platform = True

    def check_ground_collision(self, ground_group):
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground:
            self.position.y = touched_ground[0].rect.top
            self.velocity.y = 0
            self.on_ground = True

    def check_for_screen_border_collision(self):
        if self.position.x <= 0:
            self.position.x = 0
        if self.position.x + self.rect.width >= settings.WINDOW_WIDTH:
            self.position.x = settings.WINDOW_WIDTH - self.rect.width

    # We only allow the player to jump when he collides a platform or the ground.
    # But we have to specify that the jumps is enabled only when the player is over the object.
    # (The collision between the bottom of the player and the top of the object)
    def player_jump(self, ground_group, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        consition_1 = touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + settings.PLATFORM_HEIGHT // 2
        condition_2 = touched_ground and self.rect.bottom <= touched_ground[0].rect.top + settings.GROUND_HEIGHT // 2

        # The player needs to collide with the object and the player's bottom needs to be at least
        # half the object's height over the objeect (to avoid jumping bugs).
        if consition_1 or condition_2:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH
    
    def animate(self, list_of_images, animation_speed):
        if self.current_image_index < len(list_of_images) - 1:
            self.current_image_index += 1
        else:
            self.current_image_index = 0
        raw_image = list_of_images[self.current_image_index]
        self.image = pygame.transform.scale(raw_image, (self.draw_width, self.draw_height))

class Baddies(Entity):
    def __init__ (self, BADDIE_IMAGE):
        image = BADDIE_IMAGE
        self.size = random.randint(settings.BADDIE_MIN_SIZE, settings.BADDIE_MAX_SIZE)
        super().__init__(image, self.size, self.size)

        # Set the Baddie's position randomly
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(0, settings.WINDOW_HEIGHT - self.size)

        # Set the Baddie's speed randomly
        self.speed = random.randint(settings.BADDIE_MIN_SPEED, settings.BADDIE_MAX_SPEED)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Platform(Entity):
    def __init__ (self, PLATFORM_IMAGE):
        image = PLATFORM_IMAGE
        self.height = settings.PLATFORM_HEIGHT
        self.width = settings.PLATFORM_WIDTH
        super().__init__(image, self.width, self.height)

        self.rect.left = settings.WINDOW_WIDTH
        self.rect.top = random.randint(0, settings.WINDOW_HEIGHT - self.height)

    def update(self):
        self.rect.x -= settings.PLATFORM_SPEED
        if self.rect.right < 0:
            self.kill()

class Ground(Entity):
    def __init__(self, GROUND_IMAGE):
        image = GROUND_IMAGE
        self.width = settings.WINDOW_WIDTH
        self.height = settings.GROUND_HEIGHT
        super().__init__(image, self.width, self.height)

        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT)

class Background(Entity):
    def __init__(self, image, scrolling_speed, x, y):
        self.width = settings.WINDOW_WIDTH
        self.height = settings.WINDOW_HEIGHT
        super().__init__(image, self.width, self.height)

        self.speed = scrolling_speed
        self.rect.topleft = (x, y)

    def update(self):
        self.rect.x -= self.speed        
        # If the image has scrolled entirely off the left of the screen,
        # reset its position to be directly to the right the screen (for seamless looping).
        if self.rect.right <= 0:
            self.rect.left = settings.WINDOW_WIDTH
    