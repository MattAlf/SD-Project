import pygame
from pygame.locals import *
from functions import terminate
from settings import settings
import random


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, image_width, image_height):
        super().__init__()
        scaled = pygame.transform.scale(image, (image_width, image_height))
        # Convert scaled surfaces for faster blitting.
        try:
            scaled = scaled.convert_alpha()
        except pygame.error:
            scaled = scaled.convert()
        self.image = scaled
        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.current_image_index = 0
        self.player_images = settings.PLAYER_SCALED_IMAGES

        original_image = self.player_images['PLAYER_IDLE_RIGHT'][0]
        self.draw_height = settings.PLAYER_DRAW_HEIGHT
        self.draw_width = settings.PLAYER_DRAW_WIDTH
        self.image = original_image

        hitbox_width = int(self.draw_width * settings.PLAYER_HITBOX_IMAGE_WIDTH_FACTOR)
        hitbox_height = int(self.draw_height * settings.PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR)
        self.HITBOX_X_OFFSET = int(self.draw_width * settings.PLAYER_HITBOX_X_OFFSET_FACTOR)
        self.HITBOX_Y_OFFSET = int(self.draw_height * settings.PLAYER_HITBOX_Y_OFFSET_FACTOR)
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT - settings.PLATFORM_HEIGHT)
        self.full_image_rect = self.image.get_rect()
        self.full_image_rect.bottomleft = (
            self.rect.left - self.HITBOX_X_OFFSET,
            self.rect.bottom + self.HITBOX_Y_OFFSET,
        )

        self.position = pygame.math.Vector2(self.rect.left, self.rect.bottom)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.HORIZONTAL_ACCELERATION = settings.HORIZONTAL_ACCELERATION
        self.HORIZONTAL_FRICTION = settings.HORIZONTAL_FRICTION
        self.VERTICAL_ACCELERATION = settings.VERTICAL_ACCELERATION
        self.PLAYER_JUMP_STRENGTH = settings.PLAYER_JUMP_STRENGTH

        self.attack_cooldown = settings.SPEAR_ATTACK_COOLDOWN
        self.last_attack_time = 0
        self.lives = settings.PLAYER_STARTING_LIVES
        self.invulnerability_timer = 0
        self.shield_timer = 0
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

    def handle_input(self, events, ground_group, platform_group, spear_group):
        for event in events:
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key in (K_SPACE, K_UP, K_w) and (self.on_ground or self.on_platform):
                    self.jump(ground_group, platform_group)
                if event.key in (K_DOWN, K_s) and (not self.attack_left and not self.attack_right):
                    self.attack(spear_group)

        keys = pygame.key.get_pressed()
        self.run_left = keys[K_LEFT] or keys[K_a]
        self.run_right = keys[K_RIGHT] or keys[K_d]
        if self.run_left and self.run_right:
            self.run_left = self.run_right = False

    def update(self, events, ground_group, platform_group, spear_group, baddie_group, shield_pickup_group, shield_effect_group):
        self.current_time = pygame.time.get_ticks()
        self.handle_input(events, ground_group, platform_group, spear_group)
        self.acceleration = pygame.math.Vector2(0, self.VERTICAL_ACCELERATION)
        if self.run_left or self.run_right:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION if self.run_right else -self.HORIZONTAL_ACCELERATION

        if self.attack_right or self.attack_left:
            images = self.player_images['PLAYER_ATTACK_RIGHT'] if self.attack_right else self.player_images['PLAYER_ATTACK_LEFT']
            self.animate(images, settings.PLAYER_ANIMATION_SLOWER)
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

        self.check_for_pickable_objects_collision(shield_pickup_group, shield_effect_group)
        self.check_for_enemy_collision(baddie_group)

    def check_platform_collisions(self, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        if touched_platforms and self.velocity.y > 0 and self.rect.bottom < touched_platforms[0].rect.bottom:
            self.position.y = touched_platforms[0].rect.top
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
        condition_platform = touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + settings.PLATFORM_HEIGHT // 2
        condition_ground = touched_ground and self.rect.bottom <= touched_ground[0].rect.top + settings.GROUND_HEIGHT // 2
        if condition_platform or condition_ground:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.on_platform = False
            self.in_a_jump = True

    def attack(self, spear_group):
        current_time = getattr(self, "current_time", pygame.time.get_ticks())
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            if self.velocity.x > 0:
                current_direction = 1
                self.attack_right = True
            else:
                current_direction = -1
                self.attack_left = True
            start_x = self.rect.centerx
            start_y = self.rect.centery
            new_spear = Bullet(start_x, start_y, current_direction, settings.SPEAR_IMAGE)
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
            shield_effect_group.add(ShieldEffect(self, settings.SHIELD_EFFECT_IMAGE))

    def check_for_enemy_collision(self, baddie_group):
        touched_enemy = pygame.sprite.spritecollide(self, baddie_group, True)
        if touched_enemy:
            self.take_damage()

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


class Bullet(pygame.sprite.Sprite):
    kill_count = 0  # Add this class attribute
    
    def __init__(self, position_x, position_y, direction, spear_image):
        super().__init__()
        original_image = spear_image
        target_width = settings.SPEAR_WIDTH
        original_width = original_image.get_width()
        original_height = original_image.get_height()
        scale_factor = target_width / original_width
        self.draw_width = target_width
        self.draw_height = int(original_height * scale_factor)
        self.image = pygame.transform.scale(original_image, (self.draw_width, self.draw_height))
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (position_x, position_y)
        self.speed = settings.SPEAR_SPEED
        self.direction = direction

    def update(self, baddie_group):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH:
            self.kill()
        if pygame.sprite.spritecollide(self, baddie_group, True):
            self.kill()
            Bullet.kill_count += 1             


class ShieldPickup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(
            settings.SHIELD_PICKUP_IMAGE,
            (settings.SHIELD_PICKUP_SIZE, settings.SHIELD_PICKUP_SIZE)
        )
        self.rect = self.image.get_rect()
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(settings.SHIELD_PICKUP_SIZE, settings.WINDOW_HEIGHT - settings.GROUND_HEIGHT)
        self.speed = settings.SHIELD_PICKUP_SCROLL_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class ShieldEffect(pygame.sprite.Sprite):
    def __init__(self, player, shield_image):
        super().__init__()
        size = player.rect.height + 10
        self.image = pygame.transform.scale(shield_image, (size, size))
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
        self.image = pygame.transform.scale(settings.DRAGON_IMAGE, (settings.DRAGON_WIDTH, settings.DRAGON_HEIGHT))
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
        
    def update(self, fireball_group, spear_group, score):
        current_time = pygame.time.get_ticks()
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
        for spear in hit_spears:
            self.health -= 1
            if self.health <= 0:
                self.kill()


class Fireball(pygame.sprite.Sprite):
    def __init__(self, position_x, position_y, direction_x, direction_y, fireball_image, score):
        super().__init__()
        # Redimensionner l'image
        self.image = pygame.transform.scale(fireball_image, (settings.FIREBALL_SIZE, settings.FIREBALL_SIZE))
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

class Baddies(Entity):
    def __init__(self):
        image = settings.BADDIE_IMAGE
        self.size = random.randint(settings.BADDIE_MIN_SIZE, settings.BADDIE_MAX_SIZE)
        super().__init__(image, self.size* 2, self.size)
        self.rect.left = settings.WINDOW_WIDTH
        self.rect.bottom = random.randint(0, settings.WINDOW_HEIGHT - self.size)
        self.speed = random.randint(settings.BADDIE_MIN_SPEED, settings.BADDIE_MAX_SPEED)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Platform(Entity):
    def __init__(self):
        image = settings.PLATFORM_IMAGE
        self.height = settings.PLATFORM_HEIGHT
        self.width = random.randint(settings.PLATFORM_WIDTH/2, settings.PLATFORM_WIDTH)
        super().__init__(image, self.width, self.height)
        self.rect.left = random.randint(settings.WINDOW_WIDTH, settings.WINDOW_WIDTH + self.width)
        self.rect.top = random.randint(300, settings.WINDOW_HEIGHT - self.height*3)
        

    def update(self):
        self.rect.x -= settings.PLATFORM_SPEED
        if self.rect.right < 0:
            self.kill()


class Ground(Entity):
    def __init__(self):
        image = settings.GROUND_IMAGE
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
        if self.rect.right <= 0:
            self.rect.left = settings.WINDOW_WIDTH
