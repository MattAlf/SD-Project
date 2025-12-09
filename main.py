# main.py
import pygame
import sys
from pygame.locals import *
from settings import *
from functions import *
from entity import *
from entity import Ground


# Initialize Pygame.
pygame.init()

# Set up display, window name, clock, font.
window_surface = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
pygame.display.set_caption('Dodger')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Game related images. The images are converted so that the computer can draw more efficiently.
BADDIE_IMAGE = pygame.image.load('baddie.png').convert_alpha()
PLATFORM_IMAGE = pygame.image.load('platform.png').convert_alpha()
SPEAR_IMAGE = pygame.image.load('spear.png').convert_alpha()
SHIELD_EFFECT_IMAGE = pygame.image.load('shield_effect.png').convert_alpha()
SHIELD_PICKUP_IMAGE = pygame.image.load('shield_pickup.png').convert_alpha()
RED_HEART_IMAGE = pygame.image.load('red_heart.png').convert_alpha()
RED_HEART_IMAGE = pygame.transform.scale(RED_HEART_IMAGE, (settings.PLAYER_LIVES_DISPLAY_SIZE, settings.PLAYER_LIVES_DISPLAY_SIZE))
BLUE_HEART_IMAGE = pygame.image.load('blue_heart.png').convert_alpha()
BLUE_HEART_IMAGE = pygame.transform.scale(BLUE_HEART_IMAGE, (settings.PLAYER_LIVES_DISPLAY_SIZE, settings.PLAYER_LIVES_DISPLAY_SIZE))

# The player is animated. So in order to store all of the different animations we created a dictionary.
# Each key gives acces to the list with all of the images related to this action. We also had to flip the images
# to have an animation whether the player is facing right or left.
PLAYER_IMAGES = {
    'PLAYER_RUN_RIGHT' : [],
    'PLAYER_RUN_LEFT' : [],
    'PLAYER_ATTACK_RIGHT' : [],
    'PLAYER_ATTACK_LEFT' : [],
    'PLAYER_DIE_RIGHT' : [],
    'PLAYER_DIE_LEFT' : [],
    'PLAYER_HURT_RIGHT' : [],
    'PLAYER_HURT_LEFT' : [],
    'PLAYER_IDLE_RIGHT' : [],
    'PLAYER_IDLE_LEFT' : [],
    'PLAYER_JUMP_RIGHT' : [],
    'PLAYER_JUMP_LEFT' : []
}
for player_action in PLAYER_IMAGES.keys():
    if 'RUN_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_run_images/Knight_01__RUN_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_RUN_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_RUN_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
    elif 'ATTACK_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_attack_images/Knight_01__ATTACK_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_ATTACK_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_ATTACK_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
    elif 'DIE_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_die_images/Knight_01__DIE_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_DIE_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_DIE_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
    elif 'HURT_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_hurt_images/Knight_01__HURT_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_HURT_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_HURT_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
    elif 'IDLE_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_idle_images/Knight_01__IDLE_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_IDLE_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_IDLE_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
    elif 'JUMP_RIGHT' in player_action:
        for i in range(10):
            temporary_image = pygame.image.load('player_animations/player_jump_images/Knight_01__JUMP_00%s.png' % (i)).convert_alpha()
            PLAYER_IMAGES['PLAYER_JUMP_RIGHT'].append(temporary_image)
            PLAYER_IMAGES['PLAYER_JUMP_LEFT'].append(pygame.transform.flip(temporary_image, True, False))
                                
# Tuples of the background image layer associated wiht its scrolling speed. The images are converted so that the computer can draw more efficiently.
# If we don't do that the game will start lagging. The images are made to loop horizontally to make the effect of an infinite image.
BACKGROUND_IMAGES_AND_SPEEDS = [
    (pygame.image.load('background_layers/1_sky.png').convert_alpha(), settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/2_clouds.png').convert_alpha(), 2 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/3_mountain.png').convert_alpha(), settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/4_clouds.png').convert_alpha(), 3 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/5_ground.png').convert_alpha(), 4 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/6_ground.png').convert_alpha(), 7 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/7_ground.png').convert_alpha(), 8 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
    (pygame.image.load('background_layers/8_plant.png').convert_alpha(), 8 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR)
    ]
# Ground image. It is drawn separately because it will be drawn in the foreground.
GROUND_IMAGE_AND_SPEED = (pygame.image.load('background_layers/ground.png').convert_alpha(), 10 * settings.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR)
# Set up sounds.
game_over_sound = pygame.mixer.Sound('gameover.wav')
pygame.mixer.music.load('background.mid')

# Show the "Start" screen.

# Creates the group that will hold all of the background layers.
background_group = pygame.sprite.Group()
# Creates all of the background layers with the Background class constructor. Each time the constructor is called
# it creates all of the layers at the same position and stores the speed of the layer with the correct image for that layer.
# It happens because BACKGROUND_IMAGES_AND_SPEEDS is a list of tuples (layer_image, layer_speed) for each layer. The constructor
# is called 3 times because we create the current background on the screen and 2 background in advamce. That way, when the images
# scroll it seems like it's a continuous image.
for image, scrolling_speed in BACKGROUND_IMAGES_AND_SPEEDS:
    background_group.add(Background(image, scrolling_speed, 0, 0))
    background_group.add(Background(image, scrolling_speed, settings.WINDOW_WIDTH, 0))
    background_group.add(Background(image, scrolling_speed, 2 * settings.WINDOW_WIDTH, 0))
# Draws the background on the window surface.
background_group.draw(window_surface)
# Draws the ground in the foreground. It will be useful to store it in a separate group because we will draw th player between
# the background and the ground.
ground_group = pygame.sprite.Group()
test_ground = Ground(GROUND_IMAGE_AND_SPEED[0], 0, 0, 0)
for index in range(0,6):
    ground_group.add(Ground(GROUND_IMAGE_AND_SPEED[0], GROUND_IMAGE_AND_SPEED[1], index * test_ground.draw_width, settings.WINDOW_HEIGHT))
for ground in ground_group:
    window_surface.blit(ground.image, ground.full_image_rect)
# Draws the text on the starting screen.
draw_text('Dodger', font, window_surface, settings.WINDOW_WIDTH // 3, settings.WINDOW_HEIGHT // 3)
draw_text('Press a key to start.', font, window_surface, settings.WINDOW_WIDTH // 3, (settings.WINDOW_HEIGHT // 3) + 50)
# Updates the window surface so that the player sees what has been drawn until now.
pygame.display.update()

# Wait for the player to press a key to start.
wait_for_player_to_press_key()


# First game loop
while True:
    # Start a new game
    player = Player(PLAYER_IMAGES)
    player_group = pygame.sprite.GroupSingle(player)
    spear_group = pygame.sprite.Group()
    baddie_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    shield_effect_group = pygame.sprite.Group()
    shield_pickup_group = pygame.sprite.Group()
    player_group.draw(window_surface)
    score = 0
    baddie_add_counter = 0
    platform_add_counter = 0
    shield_spawn_timer = 0
    pygame.mixer.music.play(-1, 0.0)

    # Second game loop
    while not player.dead:
        score += 1

        # Add new baddies
        baddie_add_counter += 1
        if baddie_add_counter >= settings.ADD_NEW_BADDIE_RATE:
            baddie_add_counter = 0
            baddie_group.add(Baddies(BADDIE_IMAGE))

        # Add new platform 
        platform_add_counter += 1
        if platform_add_counter >= settings.ADD_NEW_PLATFORM_RATE:
            platform_add_counter = 0
            platform_group.add(Platform(PLATFORM_IMAGE))

        # Apparition aléatoire du bouclier (basé sur le temps ou le score)
        shield_spawn_timer += 1
        if shield_spawn_timer >= 100:
            shield_spawn_timer = 0
            # Ajoutez le bouclier ramassable au groupe
            shield_pickup_group.add(ShieldPickup(SHIELD_PICKUP_IMAGE))

        # Update game objects
        platform_group.update()
        player_group.update(ground_group, platform_group, spear_group, SPEAR_IMAGE, baddie_group, shield_pickup_group, shield_effect_group, SHIELD_EFFECT_IMAGE)
        baddie_group.update()
        spear_group.update(baddie_group)
        background_group.update()
        ground_group.update()
        shield_effect_group.update()
        shield_pickup_group.update()

        # Draw everything
        background_group.draw(window_surface)
        draw_text('Score: %s' % (score), font, window_surface, 10, 0)
        window_surface.blit(player.image, player.full_image_rect)
        baddie_group.draw(window_surface)
        platform_group.draw(window_surface)
        spear_group.draw(window_surface)
        for ground in ground_group:
            window_surface.blit(ground.image, ground.full_image_rect)
        shield_effect_group.draw(window_surface)
        shield_pickup_group.draw(window_surface)
        
        # Draws the number of lives the player has left
        for i in range(player.lives):
            heart_left = settings.WINDOW_WIDTH - settings.PLAYER_LIVES_MARGIN_X - (settings.PLAYER_LIVES_DISPLAY_SIZE * (i + 1)) - (settings.PLAYER_LIVES_HEART_SPACING * i)
            if player.has_shield:
                window_surface.blit(BLUE_HEART_IMAGE, (heart_left, settings.PLAYER_LIVES_MARGIN_Y))
            else:
                window_surface.blit(RED_HEART_IMAGE, (heart_left, settings.PLAYER_LIVES_MARGIN_Y))

        # Update display inside the game
        pygame.display.update()

        # Control FPS
        clock.tick(settings.FPS)
    
    # Shows the game over screen
    pygame.mixer.music.stop()
    game_over_sound.play()
    game_over_text(window_surface)
    pygame.display.update()
    wait_for_player_to_press_key()
    game_over_sound.stop()
