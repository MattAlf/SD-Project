import pygame
from pygame.locals import *
from settings import settings
import random


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # The current image index will be useful to iterate through the animations
        self.current_image_index = 0
        self.player_images = settings.PLAYER_IMAGES

        original_image = self.player_images['PLAYER_IDLE_RIGHT'][0]
        self.draw_height = original_image.get_height()
        self.draw_width = original_image.get_width()
        self.image = original_image

        # Define hitbox around the armor, ignoring the spear, cape, and empty image space.
        hitbox_width = int(self.draw_width * settings.PLAYER_HITBOX_IMAGE_WIDTH_FACTOR)
        hitbox_height = int(self.draw_height * settings.PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR)
        
        # Calculate offset to center the hitbox on the visual sprite
        self.HITBOX_X_OFFSET = int(self.draw_width * settings.PLAYER_HITBOX_X_OFFSET_FACTOR)
        self.HITBOX_Y_OFFSET = int(self.draw_height * settings.PLAYER_HITBOX_Y_OFFSET_FACTOR)
        
        # Create the hitbox rectangle and set starting position
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT - settings.GROUND_HEIGHT)
        
        # The rect for the full visual image (larger than hitbox).
        self.full_image_rect = self.image.get_rect()
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)

        # Kinematic vectors (x,y)
        self.position = pygame.math.Vector2(self.rect.left, self.rect.bottom)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # Kinematic constants.
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGTH = settings.PLAYER_JUMP_STRENGTH
        
        # Attack cooldown timers
        self.attack_cooldown = settings.SPEAR_ATTACK_COOLDOWN
        self.last_attack_time = 0

        # Lives and Shield status
        self.lives = settings.PLAYER_STARTING_LIVES
        self.invulnerability_timer = 0
        self.shield_timer = 0
        
        # State flags
        self.has_shield = False
        self.is_invulnerable = False
        self.dead = False
        self.run_left = False
        self.run_right = False
        self.in_a_jump = False
        self.on_ground = False
        self.on_platform = False
        self.attack_right = False
        self.attack_left = False
        self.drop_through = False

    def update(self, current_time, ground_group, platform_group):
        self.current_time = current_time
        
        # Apply gravity.
        self.acceleration = pygame.math.Vector2(0, self.VERTICAL_ACCELERATION)
        
        # Apply horizontal movement based on input.
        if self.run_right:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
        elif self.run_left:
            self.acceleration.x = -self.HORIZONTAL_ACCELERATION

        # Handle Animation state selection
        if self.attack_right or self.attack_left:
            if self.attack_right:
                self.animate(self.player_images['PLAYER_ATTACK_RIGHT'])
            else:
                self.animate(self.player_images['PLAYER_ATTACK_LEFT'])
        elif self.in_a_jump:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_JUMP_RIGHT'])
            else:
                self.animate(self.player_images['PLAYER_JUMP_LEFT'])
        elif self.run_left or self.run_right:
            if self.run_right:
                self.animate(self.player_images['PLAYER_RUN_RIGHT'])
            else:
                self.animate(self.player_images['PLAYER_RUN_LEFT'])
        else:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_IDLE_RIGHT'])
            else:
                self.animate(self.player_images['PLAYER_IDLE_LEFT'])

        # Apply friction and update physics.
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Update position and sync image to hitbox
        self.check_for_screen_border_collision()
        self.rect.bottomleft = self.position
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)
        
        # Collision checks.
        self.check_platform_collisions(platform_group)
        self.check_ground_collision(ground_group)

        # Handle shield expiration.
        if self.has_shield and self.current_time > self.shield_timer:
            self.has_shield = False

        # Handle invulnerability flashing effect
        if self.is_invulnerable:
            if self.current_time > self.invulnerability_timer:
                self.is_invulnerable = False
                self.image.set_alpha(255)
            else:
                # Flash sprite transparency
                self.image.set_alpha(0 if self.current_time // 100 % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)

    def check_platform_collisions(self, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        # Land on platform only if falling down and not dropping through.
        if touched_platforms and not self.drop_through and self.velocity.y > 0 and self.rect.bottom < touched_platforms[0].rect.bottom:
            self.position.y = touched_platforms[0].rect.top
            # Move player with the platform speed if idle
            if not (self.run_right or self.run_left):
                self.position.x -= settings.PLATFORM_SPEED
            self.velocity.y = 0
            self.on_platform = True
            self.in_a_jump = False
        else:
            self.on_platform = False

    def check_ground_collision(self, ground_group):
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground:
            self.position.y = touched_ground[0].rect.top
            # Move player with the ground speed if idle.
            if not (self.run_right or self.run_left):
                self.position.x -= settings.GROUND_IMAGE_AND_SPEED[1]
            self.velocity.y = 0
            self.on_ground = True
            self.in_a_jump = False
        else:
            self.on_ground = False

    def check_for_screen_border_collision(self):
        if self.position.x <= 0:
            self.position.x = 0
        if self.position.x + self.rect.width >= settings.WINDOW_WIDTH:
            self.position.x = settings.WINDOW_WIDTH - self.rect.width

    def jump(self, ground_group, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        
        # Check if standing on platform or ground with tolerance
        condition_platform = touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + settings.PLATFORM_HEIGHT // 2
        condition_ground = touched_ground and self.rect.bottom <= touched_ground[0].rect.top + settings.GROUND_HEIGHT // 2
        
        if condition_platform or condition_ground:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.on_platform = False
            self.in_a_jump = True

    def attack(self, spear_group):
        if self.current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = self.current_time
            # Determine direction based on velocity
            if self.velocity.x > 0:
                current_direction = 1
                self.attack_right = True
            else:
                current_direction = -1
                self.attack_left = True
            
            # Spawn spear
            start_x = self.rect.centerx
            start_y = self.rect.centery
            settings.ALL_SOUND_EFFECTS['SPEAR_THROW'].play()
            new_spear = Spear(start_x, start_y, current_direction)
            spear_group.add(new_spear)

    def animate(self, list_of_images):
        # Cycle through animation frames.
        if self.current_image_index < settings.PLAYER_ANIMATION_SLOWER * len(list_of_images) - 1:
            self.current_image_index += 1
        else:
            self.current_image_index = 0
        
        raw_image = list_of_images[self.current_image_index // settings.PLAYER_ANIMATION_SLOWER]
        self.image = raw_image
        
        # Reset attack flag when animation finishes.
        if (self.attack_left or self.attack_right) and self.current_image_index == settings.PLAYER_ANIMATION_SLOWER * len(list_of_images) - 1:
            self.attack_right = False
            self.attack_left = False

    def check_for_pickable_objects_collision(self, shield_pickup_group, shield_effect_group):
        collected_shield_object = pygame.sprite.spritecollide(self, shield_pickup_group, True)
        if collected_shield_object and not self.has_shield:
            settings.ALL_SOUND_EFFECTS['SHIELD_PICKUP'].play()
            self.has_shield = True
            self.shield_timer = self.current_time + settings.SHIELD_DURATION_TIME
            shield_effect_group.add(ShieldEffect(self))

    def check_for_enemy_collision(self, ghost_group, fireball_group, dragon_group):
        # Check collision with enemies/projectiles.
        touched_ghost = pygame.sprite.spritecollide(self, ghost_group, True)
        touched_fireball = pygame.sprite.spritecollide(self, fireball_group, True)
        touched_dragon = pygame.sprite.spritecollide(self, dragon_group, False)
        
        if touched_ghost or touched_fireball:
            settings.ALL_SOUND_EFFECTS['SHIELD_BREAK'].play()
            self.take_damage()
        if touched_dragon:
            settings.ALL_SOUND_EFFECTS['SHIELD_BREAK'].play()
            self.take_damage()
            # Knockback effect upon hitting the dragon
            if self.velocity.x > 0 and self.velocity.y > 0:
                self.position.x -= 20
                self.position.y -= 20
            if self.velocity.x > 0 and self.velocity.y < 0:
                self.position.x -= 20
                self.position.y += 20
            if self.velocity.x < 0 and self.velocity.y > 0:
                self.position.x += 20
                self.position.y -= 20
            if self.velocity.x < 0 and self.velocity.y < 0:
                self.position.x += 20
                self.position.y += 20

    def take_damage(self):
        if self.has_shield:
            settings.ALL_SOUND_EFFECTS['SHIELD_BREAK'].play()
            self.has_shield = False
            return
        if not self.is_invulnerable:
            settings.ALL_SOUND_EFFECTS['PLAYER_HIT'].play()
            self.lives -= 1
            if self.lives > 0:
                self.is_invulnerable = True
                self.invulnerability_timer = self.current_time + settings.PLAYER_INVULNERABILITY_TIME
            else:
                self.dead = True


class Spear(pygame.sprite.Sprite):
    kill_count = 0  
    
    def __init__(self, position_x, position_y, direction):
        super().__init__()
        self.image = settings.SPEAR_IMAGE
        # Flip image if throwing left
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (position_x, position_y)
        self.speed = settings.SPEAR_SPEED
        self.direction = direction

    def update(self, ghost_group):
        self.rect.x += self.speed * self.direction
        # Remove spear if it goes off-screen.
        if self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH:
            self.kill()
        # Check collision with ghosts.
        if pygame.sprite.spritecollide(self, ghost_group, True):
            settings.ALL_SOUND_EFFECTS['KILL'].play()
            self.kill()
            Spear.kill_count += 1

class ShieldPickup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = settings.SHIELD_PICKUP_IMAGE
        self.rect = self.image.get_rect()
        # Spawn off-screen to the right at random height.
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(settings.SHIELD_PICKUP_SIZE, settings.WINDOW_HEIGHT - settings.GROUND_HEIGHT)
        self.speed = settings.SHIELD_PICKUP_SCROLL_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class ShieldEffect(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = settings.SHIELD_EFFECT_IMAGE
        self.rect = self.image.get_rect()
        self.player = player

    def update(self):
        # Follow the player position.
        self.rect.center = self.player.rect.center
        if not self.player.has_shield:
            self.kill()

class Dragon(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Image and display.
        self.image = settings.DRAGON_IMAGE
        self.rect = self.image.get_rect()
        self.rect.centerx = settings.WINDOW_WIDTH // 2
        self.rect.top = 50 
        
        # Vertical flight speed.
        self.speed_y = 2
        self.direction_y = 1  # 1 for down, -1 for up
        
        # Player reference for targeting.
        self.player = player
        
        # Fireball shooting mechanics.
        self.attack_cooldown = settings.DRAGON_ATTACK_COOLDOWN 
        self.last_attack_time = 0
        
        # Dragon health.
        self.health = 3
        
    def update(self, current_time, fireball_group, spear_group, score):
        self.score = score
        # Vertical movement (oscillates in the upper area).
        self.rect.y += self.speed_y * self.direction_y
        
        # Bounce when hitting vertical boundaries.
        if self.rect.top <= 30:
            self.direction_y = 1
        elif self.rect.bottom >= settings.WINDOW_HEIGHT // 2: 
            self.direction_y = -1
        
        # Shoot fireballs towards the player
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            
            # Calculate vector distance to player
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            
            # Create fireball.
            settings.ALL_SOUND_EFFECTS['DRAGON_ATTACK'].play()
            fireball = Fireball(self.rect.centerx, self.rect.centery, dx - 20, dy, settings.FIREBALL_IMAGE, score)
            fireball_group.add(fireball)
        
        # Check for spear collisions.
        hit_spears = pygame.sprite.spritecollide(self, spear_group, True)
        if hit_spears:
            settings.ALL_SOUND_EFFECTS['KILL'].play()
            self.health -= 1
            if self.health <= 0:
                self.kill()


class Fireball(pygame.sprite.Sprite):
    def __init__(self, position_x, position_y, direction_x, direction_y, fireball_image, score):
        super().__init__()
        self.image = settings.FIREBALL_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (position_x, position_y)
        
        # Calculate velocity vector (normalized)
        magnitude = (direction_x**2 + direction_y**2)**0.5
        if magnitude > 0:
            # Scale speed based on score.
            self.speed_x = (direction_x / magnitude) * settings.FIREBALL_SPEED * int(score/1000)
            self.speed_y = (direction_y / magnitude) * settings.FIREBALL_SPEED * int(score/1000)
        else:
            self.speed_x = self.speed_y = 0
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Kill if out of screen bounds
        if (self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > settings.WINDOW_HEIGHT):
            self.kill()

class Ghosts(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = settings.GHOST_IMAGE
        # Randomize size and spawn height.
        self.size = random.randint(settings.GHOST_MIN_SIZE, settings.GHOST_MAX_SIZE)
        self.image = pygame.transform.scale(original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(0, settings.WINDOW_HEIGHT - (settings.GROUND_HEIGHT + self.size))
        # Randomize speed.
        self.speed = random.randint(settings.GHOST_MIN_SPEED, settings.GHOST_MAX_SPEED)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = settings.PLATFORM_IMAGE
        self.height = settings.PLATFORM_HEIGHT
        self.width = random.randint(settings.PLATFORM_WIDTH // 2, settings.PLATFORM_WIDTH)
        self.image = pygame.transform.scale(original_image, (self.width, self.height))
        # Spawn off-screen with random height
        self.rect = self.image.get_rect()
        self.rect.left = random.randint(settings.WINDOW_WIDTH, settings.WINDOW_WIDTH + self.width)
        self.rect.top = random.randint(300, settings.WINDOW_HEIGHT - self.height*3)
        
    def update(self):
        self.rect.x -= settings.PLATFORM_SPEED
        if self.rect.right < 0:
            self.kill()

class Ground(pygame.sprite.Sprite):
    def __init__(self, ground_number):
        super().__init__()
        self.image, self.speed = settings.GROUND_IMAGE_AND_SPEED

        self.draw_width = self.image.get_width()
        self.draw_height = self.image.get_height()

        hitbox_width = self.draw_width
        hitbox_height = int(self.draw_height * settings.GROUND_HITBOX_IMAGE_HEIGHT_FACTOR)
     
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.bottomleft = (ground_number * self.draw_width, settings.WINDOW_HEIGHT)

        self.full_image_rect = self.image.get_rect()
        self.full_image_rect.bottomleft = self.rect.bottomleft

    def update(self):
        self.rect.x -= self.speed
        self.full_image_rect.x -= self.speed
        # If ground goes off-screen left, move it to the far right to create infinite loop
        if self.rect.right <= 0 and self.full_image_rect.right <= 0:
            self.rect.left += 5 * self.draw_width
            self.full_image_rect.left += 5 * self.draw_width
            
class Background(pygame.sprite.Sprite):
    def __init__(self, image, scrolling_speed, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.speed = scrolling_speed
        self.rect.topleft = (x, y)

    def update(self):
        self.rect.x -= self.speed
        # Parallax scrolling: reset position when off-screen
        if self.rect.right <= 0:
            self.rect.left = settings.WINDOW_WIDTH