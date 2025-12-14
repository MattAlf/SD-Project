import pygame
from pygame.locals import *
from settings import settings, terminate
import random


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # The current image index will be useful to iterate through the animations.
        self.current_image_index = 0
        self.player_images = settings.PLAYER_IMAGES

        original_image = self.player_images['PLAYER_IDLE_RIGHT'][0]
        self.draw_height = original_image.get_height()
        self.draw_width = original_image.get_width()
        self.image = original_image

        # We define the hitbox of the player. We want the hitbox to be around the player's armor and it should
        # not take into account the spear nor the cape of the player. Also the image has quite a lot of empty space
        # around the knight, so we want to ignore that.
        hitbox_width = int(self.draw_width * settings.PLAYER_HITBOX_IMAGE_WIDTH_FACTOR)
        hitbox_height = int(self.draw_height * settings.PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR)
        # Here we define the hitbox offset. In order to center the hitbox (which will be a basic rectangle) on
        # the player's image, we have to calculate by how much we have to shift the image before we draw it in
        # order to have the hitbox and the knight drawn inside of it.
        self.HITBOX_X_OFFSET = int(self.draw_width * settings.PLAYER_HITBOX_X_OFFSET_FACTOR)
        self.HITBOX_Y_OFFSET = int(self.draw_height * settings.PLAYER_HITBOX_Y_OFFSET_FACTOR)
        # Here the rectangle that represents the hitbox is drawn.
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        # The rectangle (hitbox) is repositioned to the left of the screen. (player's starting position)
        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT - settings.GROUND_HEIGHT)
        # This is the rectangle associated with the full image. So it has also the empty spaces around it.
        self.full_image_rect = self.image.get_rect()
        # Here we reposition the image to place the knight inside of the hitbox.
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)

        # Kinematic vectors (x,y).
        self.position = pygame.math.Vector2(self.rect.left, self.rect.bottom)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        # Kinematic constants.
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGTH = settings.PLAYER_JUMP_STRENGTH
        # This is the cooldown that the player will have to wait before being able to throw another spear.
        self.attack_cooldown = settings.SPEAR_ATTACK_COOLDOWN
        # We set 0 as the initial last attack time. This allows the player to start shooting
        # 'settings.SPEAR_ATTACK_COOLDOWN' time after the beginning of the game.
        self.last_attack_time = 0

        # Setting the variables regarding the lives and shield.
        self.lives = settings.PLAYER_STARTING_LIVES
        # These two timers will be used to track when will the corresponding effect need to be disabled after being activated.
        self.invulnerability_timer = 0
        self.shield_timer = 0
        # We set the variables to false.
        self.has_shield = False
        self.is_invulnerable = False
        self.dead = False
        # We also set the movement variables to False.
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
        self.acceleration = pygame.math.Vector2(0, self.VERTICAL_ACCELERATION)
        if self.run_right:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
        elif self.run_left:
            self.acceleration.x = -self.HORIZONTAL_ACCELERATION

        if self.attack_right or self.attack_left:
            if self.attack_right:
                self.animate(self.player_images['PLAYER_ATTACK_RIGHT'], settings.PLAYER_ANIMATION_SLOWER)
            else:
                self.animate(self.player_images['PLAYER_ATTACK_LEFT'], settings.PLAYER_ANIMATION_SLOWER)
        elif self.in_a_jump:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_JUMP_RIGHT'], settings.PLAYER_ANIMATION_SLOWER)
            else:
                self.animate(self.player_images['PLAYER_JUMP_LEFT'], settings.PLAYER_ANIMATION_SLOWER)
        elif self.run_left or self.run_right:
            if self.run_right:
                self.animate(self.player_images['PLAYER_RUN_RIGHT'], settings.PLAYER_ANIMATION_SLOWER)
            else:
                self.animate(self.player_images['PLAYER_RUN_LEFT'], settings.PLAYER_ANIMATION_SLOWER)
        else:
            if self.velocity.x > 0:
                self.animate(self.player_images['PLAYER_IDLE_RIGHT'], settings.PLAYER_ANIMATION_SLOWER)
            else:
                self.animate(self.player_images['PLAYER_IDLE_LEFT'], settings.PLAYER_ANIMATION_SLOWER)

        if not self.drop_through:
            self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        self.check_for_screen_border_collision()
        self.rect.bottomleft = self.position
        self.full_image_rect.bottomleft = (
            self.rect.left - self.HITBOX_X_OFFSET,
            self.rect.bottom + self.HITBOX_Y_OFFSET,
        )
        self.check_platform_collisions(platform_group)
        self.check_ground_collision(ground_group)

        if self.has_shield and self.current_time > self.shield_timer:
            self.has_shield = False

        if self.is_invulnerable:
            if self.current_time > self.invulnerability_timer:
                self.is_invulnerable = False
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(0 if self.current_time // 100 % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)

    def check_platform_collisions(self, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        if touched_platforms and not self.drop_through and self.velocity.y > 0 and self.rect.bottom < touched_platforms[0].rect.bottom:
            self.position.y = touched_platforms[0].rect.top
            self.position.x -= settings.PLATFORM_SPEED
            self.velocity.y = 0
            self.drop_through = False
            self.on_platform = True
            self.in_a_jump = False
        else:
            self.on_platform = False

    def check_ground_collision(self, ground_group):
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground:
            self.position.y = touched_ground[0].rect.top
            self.velocity.y = 0
            self.drop_through = False
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
            if self.velocity.x > 0:
                current_direction = 1
                self.attack_right = True
            else:
                current_direction = -1
                self.attack_left = True
            start_x = self.rect.centerx
            start_y = self.rect.centery
            new_spear = Spear(start_x, start_y, current_direction)
            spear_group.add(new_spear)

    def animate(self, list_of_images, animation_speed):
        if self.current_image_index < animation_speed * len(list_of_images) - 1:
            self.current_image_index += 1
        else:
            self.current_image_index = 0
        raw_image = list_of_images[self.current_image_index // animation_speed]
        self.image = raw_image
        if (self.attack_left or self.attack_right) and self.current_image_index == animation_speed * len(list_of_images) - 1:
            self.attack_right = False
            self.attack_left = False

    def check_for_pickable_objects_collision(self, shield_pickup_group, shield_effect_group):
        collected_shield_object = pygame.sprite.spritecollide(self, shield_pickup_group, True)
        if collected_shield_object and not self.has_shield:
            self.has_shield = True
            self.shield_timer = self.current_time + settings.SHIELD_DURATION_TIME
            shield_effect_group.add(ShieldEffect(self))

    def check_for_enemy_collision(self, ghost_group, fireball_group, dragon_group):
        touched_ghost = pygame.sprite.spritecollide(self, ghost_group, True)
        touched_fireball = pygame.sprite.spritecollide(self, fireball_group, True)
        touched_dragon = pygame.sprite.spritecollide(self, dragon_group, False)
        if touched_ghost or touched_fireball:
            self.take_damage()
        if touched_dragon:
            self.take_damage()
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
            self.has_shield = False
            return
        if not self.is_invulnerable:
            self.lives -= 1
            if self.lives > 0:
                self.is_invulnerable = True
                self.invulnerability_timer = self.current_time + settings.PLAYER_INVULNERABILITY_TIME
            else:
                self.dead = True


class Spear(pygame.sprite.Sprite):
    kill_count = 0  # Add this class attribute
    
    def __init__(self, position_x, position_y, direction):
        super().__init__()
        self.image = settings.SPEAR_IMAGE
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (position_x, position_y)
        self.speed = settings.SPEAR_SPEED
        self.direction = direction

    def update(self, ghost_group):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH:
            self.kill()
        if pygame.sprite.spritecollide(self, ghost_group, True):
            self.kill()
            Spear.kill_count += 1

class ShieldPickup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = settings.SHIELD_PICKUP_IMAGE
        self.rect = self.image.get_rect()
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
        self.rect.center = self.player.rect.center
        if not self.player.has_shield:
            self.kill()

class Dragon(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Image et affichage
        self.image = settings.DRAGON_IMAGE
        self.rect = self.image.get_rect()
        self.rect.centerx = settings.WINDOW_WIDTH // 2
        self.rect.top = 50  # Haut de l'écran
        
        # Vitesse de vol (haut/bas)
        self.speed_y = 2
        self.direction_y = 1  # 1 pour bas, -1 pour haut
        
        # Joueur pour ciblage
        self.player = player
        
        # Tir de boules de feu
        self.attack_cooldown = settings.DRAGON_ATTACK_COOLDOWN  # À définir dans settings
        self.last_attack_time = 0
        
        # Santé du dragon
        self.health = 3
        
    def update(self, current_time, fireball_group, spear_group, score):
        self.score = score
        # Mouvement vertical (va et vient dans la partie supérieure)
        self.rect.y += self.speed_y * self.direction_y
        
        # Rebond quand atteint les limites
        if self.rect.top <= 30:
            self.direction_y = 1
        elif self.rect.bottom >= settings.WINDOW_HEIGHT // 2:  # Limite inférieure
            self.direction_y = -1
        
        # Tirer des boules de feu vers le joueur
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            
            # Calculer la direction vers le joueur
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            
            # Créer une boule de feu
            fireball = Fireball(self.rect.centerx, self.rect.centery, dx, dy, settings.FIREBALL_IMAGE, score)
            fireball_group.add(fireball)
        
        # Vérifier les collisions avec les spears
        hit_spears = pygame.sprite.spritecollide(self, spear_group, True)
        if hit_spears:
            self.health -= 1
            if self.health <= 0:
                self.kill()


class Fireball(pygame.sprite.Sprite):
    def __init__(self, position_x, position_y, direction_x, direction_y, fireball_image, score):
        super().__init__()
        # Redimensionner l'image
        self.image = settings.FIREBALL_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (position_x, position_y)
        

        # Vitesse (normaliser la direction)
        magnitude = (direction_x**2 + direction_y**2)**0.5
        if magnitude > 0:
            self.speed_x = (direction_x / magnitude) * settings.FIREBALL_SPEED * int(score/1000)
            self.speed_y = (direction_y / magnitude) * settings.FIREBALL_SPEED * int(score/1000)
        else:
            self.speed_x = self.speed_y = 0
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Supprimer si sortie de l'écran
        if (self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > settings.WINDOW_HEIGHT):
            self.kill()

class Ghosts(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = settings.GHOST_IMAGE
        self.size = random.randint(settings.GHOST_MIN_SIZE, settings.GHOST_MAX_SIZE)
        self.image = pygame.transform.scale(original_image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(0, settings.WINDOW_HEIGHT - (settings.GROUND_HEIGHT + self.size))
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
        if self.rect.right <= 0:
            self.rect.left = settings.WINDOW_WIDTH
