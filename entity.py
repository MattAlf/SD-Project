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
        # The current image index will be useful to iterate through the animations.
        self.current_image_index = 0
        self.player_images = PLAYER_IMAGES
        # The target height will be used to find the width of the player image that will be displayed.
        target_height = settings.PLAYER_HEIGHT

        original_image = self.player_images['PLAYER_IDLE_RIGHT'][0]
        original_width = original_image.get_width()
        original_height = original_image.get_height()
        # We define the scale factor that tells us by how much we shrank the height compared to the original image.
        # That way we will keep the original image proportions.
        scale_factor = target_height / original_height
        self.draw_height = target_height
        self.draw_width = int(original_width * scale_factor)
        # Here the image that will be displayed on the screen is created by scaling the original image.
        self.image = pygame.transform.scale(original_image, (self.draw_width, self.draw_height))
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
        self.rect.bottomleft = (0, settings.WINDOW_HEIGHT - settings.PLATFORM_HEIGHT)
        # This is the rectangle associated with the full image (but rescaled compared to the original). So
        # it has also the empty spaces around it.
        self.full_image_rect = self.image.get_rect()
        # Here we reposition the image to place the knight inside of the hitbox.
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
        # This is the cooldown that the player will have to wait before being able to throw another spear.
        self.attack_cooldown = settings.SPEAR_ATTACK_COOLDOWN
        # We set 0 as the initial last attack time. This allows the player to start shooting
        # 'settings.SPEAR_ATTACK_COOLDOWN' time after the begining of the game.
        self.last_attack_time = 0
        # We also set the movement variables to False.
        self.run_left = False
        self.run_right = False
        self.in_a_jump = False
        self.on_ground = False
        self.on_platform = False
        self.attack_right = False
        self.attack_left = False

    def handle_input(self, ground_group, platform_group, spear_group, SPEAR_IMAGE):
        # The 'red cross' at the top left of the window closes the game.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # The 'space', 'up arrow' and 'w' keys make the player jump only if he is on the ground or on a platform.
            if event.type == KEYDOWN:
                if event.key in (K_SPACE, K_UP, K_w) and (self.on_ground or self.on_platform):
                    self.jump(ground_group, platform_group)
                # The 'down arrow' and 's' keys make the player throw a spear only if he is not already attacking.
                if event.key in (K_DOWN, K_s) and (not self.attack_left or not self.attack_right):
                    self.attack(spear_group, SPEAR_IMAGE)
            # The game will close after the player clicks the 'escape' key.
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
        # Here we look at the state of the all the keys at each frame. It is useful because
        # running left or right are continuous movements.
        keys = pygame.key.get_pressed()
        # We first set the movements to False.
        self.run_left = False
        self.run_right = False
        # The 'left arrow' and 'a' keys make the player go left.
        if keys[K_LEFT] or keys[K_a]:
            self.run_left = True
        # The 'right arrow' and 'd' keys make the player go right.
        if keys[K_RIGHT] or keys[K_d]:
            self.run_right = True
        # If both movements were set to True we reset them both to False. (the forces kind of balance out)
        if self.run_left and self.run_right:
            self.run_right = self.run_left = False

    def update(self, ground_group, platform_group, spear_group, SPEAR_IMAGE):
        # Check for the player's input at each update.
        self.handle_input(ground_group, platform_group, spear_group, SPEAR_IMAGE)
        # Set the initial acceleration to (0, gravity). (gravity is always present)
        self.acceleration = pygame.math.Vector2(0, self.VERTICAL_ACCELERATION)
        # Update the horizontal acceleration of the player according to the inputs.
        if self.run_left or self.run_right:
            if self.run_right:
                self.acceleration.x = self.HORIZONTAL_ACCELERATION
            else:
                self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
        # Here we display the correct animation according to the player's movement. We display them by priority.
        # First we look if the player is attacking, then if he is jumping, then if he is running. and if he does
        # nothing then the knight will idle. To check he the player is going left or right we check the
        # player's velocity on the 'x' axis. If it is positiv it means he was or is moving right and if negative
        # it means the opposite.
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

        # Calculate the new kinematics according to the player's movements.
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Make the player stay within the window screen
        self.check_for_screen_border_collision()

        # Update the player's hitbox position and also updates the knight's image position.
        self.rect.bottomleft = self.position
        self.full_image_rect.bottomleft = (self.rect.left - self.HITBOX_X_OFFSET, self.rect.bottom + self.HITBOX_Y_OFFSET)

        # Check for collisions with the ground and the platforms. We have to put it after we
        # update the player's rectangle so that the jumping mechanics work.
        self.check_platform_collisions(platform_group)
        self.check_ground_collision(ground_group)
    
    def check_platform_collisions(self, platform_group):
        # touched_platforms will be equal to True if the player (self) is colliding with one of the platforms
        # in the platform_group (which is a sprite group). The third parameter tells us if we want to remove
        # the object that collided with the player.
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        # If the players touches a platform AND if he is falling (velocity of 'y' > 0) AND if the bottom of
        # his hitbox is higher than the bottom of the platform, THEN the player will be teleported to the top
        # of the platform. He will also be moving at the same speed as the platform and his velocity.y will
        # be set to 0. (he will stop falling). It also sets the according movement variables to True or False.
        if touched_platforms and self.velocity.y > 0 and self.rect.bottom < touched_platforms[0].rect.bottom:
            self.position.y = touched_platforms[0].rect.top
            self.position.x -= settings.PLATFORM_SPEED
            self.velocity.y = 0
            self.on_platform = True
            self.in_a_jump = False
        else:
            self.on_platform = False
    # Same principles as for the check_platform_collisions function.
    def check_ground_collision(self, ground_group):
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        if touched_ground:
            self.position.y = touched_ground[0].rect.top
            self.velocity.y = 0
            self.on_ground = True
            self.in_a_jump = False
        else:
            self.on_ground = False
    # Here we make the player stay within the window screen borders.
    def check_for_screen_border_collision(self):
        if self.position.x <= 0:
            self.position.x = 0
        if self.position.x + self.rect.width >= settings.WINDOW_WIDTH:
            self.position.x = settings.WINDOW_WIDTH - self.rect.width

    # We only allow the player to jump when he collides a platform or the ground.
    # But we have to specify that the jumps is enabled only when the player is over the object.
    # (The collision between the bottom of the player and the top of the object)
    def jump(self, ground_group, platform_group):
        touched_platforms = pygame.sprite.spritecollide(self, platform_group, False)
        touched_ground = pygame.sprite.spritecollide(self, ground_group, False)
        consition_1 = touched_platforms and self.rect.bottom <= touched_platforms[0].rect.top + settings.PLATFORM_HEIGHT // 2
        condition_2 = touched_ground and self.rect.bottom <= touched_ground[0].rect.top + settings.GROUND_HEIGHT // 2

        # The player needs to collide with the object and the player's bottom needs to be at least
        # half the object's height over the objeect (to avoid jumping bugs).
        if consition_1 or condition_2:
            self.velocity.y = -1 * self.PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.on_platform = False
            self.in_a_jump = True

    def attack(self, spear_group, SPEAR_IMAGE):
        # Here we get the current time in ticks (milliseconds).
        current_time = pygame.time.get_ticks()
        # Here we check if the cooldown is over by seeing if there is at least 'self.attack_cooldown' milliseconds
        # that separate the current time and the last attack time.
        if current_time - self.last_attack_time > self.attack_cooldown:
            # Then we set the last attack time as the current time so that the next attack attempt will be up to date.
            self.last_attack_time = current_time
            # Here we check if the player's is facing right or left and setting the varibales according to it.
            if self.velocity.x > 0:
                current_direction = 1
                self.attack_right = True
            else:
                current_direction = -1
                self.attack_left = True
            # We set the starting position of the spear at the center of the player's hitbox.
            start_x = self.rect.centerx
            start_y = self.rect.centery
            # Here we create the new spear and add it to the spear_group.
            new_spear = Bullet(start_x, start_y, current_direction, SPEAR_IMAGE)
            spear_group.add(new_spear)
        
    def animate(self, list_of_images, animation_speed):
        # To animate the knight we will go through the list of images of the associated animation and
        # then we will set the actual image of the player to the current one. And when we have gone through
        # the whole list we start again from the begining.
        # The animation_speed variable let us manipulate the speed at which we display the images by making
        # each image repeat 'animation_speed' times before going to the next one. It is because the integer
        # division (//) rounds down to the integer everytime.
        if self.current_image_index < animation_speed * len(list_of_images) - 1:
            self.current_image_index += 1
        else:
            self.current_image_index = 0
        raw_image = list_of_images[self.current_image_index // animation_speed]
        self.image = pygame.transform.scale(raw_image, (self.draw_width, self.draw_height))
        # When the player throws a spear we want to go through the animation only once.
        if (self.attack_left or self.attack_right) and self.current_image_index == animation_speed * len(list_of_images) - 1:
            self.attack_right = False
            self.attack_left = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position_x, position_y, direction, SPEAR_IMAGE):
        super().__init__()
        original_image = SPEAR_IMAGE
        target_width = settings.SPEAR_WIDTH

        original_width = original_image.get_width()
        original_height = original_image.get_height()

        scale_factor = target_width / original_width
        self.draw_width = target_width
        self.draw_height = int(original_height * scale_factor)            
        
        # Charger et redimensionner l'image de la balle
        self.image = pygame.transform.scale(original_image, (self.draw_width, self.draw_height))
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        
        # Positionner la balle au départ (par exemple, au centre du joueur)
        self.rect.center = (position_x, position_y)
        
        # Vitesse et direction (si direction est -1 pour gauche et 1 pour droite)
        self.speed = settings.SPEAR_SPEED
        self.direction = direction

    def update(self):
        # Déplacer la balle horizontalement
        self.rect.x += self.speed * self.direction
        
        # Tuer la balle si elle sort de l'écran
        if self.rect.right < 0 or self.rect.left > settings.WINDOW_WIDTH:
            self.kill()

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
    