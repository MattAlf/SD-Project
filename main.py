# main.py
import pygame
import sys
from pygame.locals import *
from settings import *
from functions import *
from entity import *
from myplatform import MyPlatform
from background import Background


# Initialize Pygame
pygame.init()
settings = Settings()

# Set up display, clock, font
window_surface = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
pygame.display.set_caption('Dodger')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Set up sounds
game_over_sound = pygame.mixer.Sound('gameover.wav')
pygame.mixer.music.load('background.mid')

# Show the "Start" screen.
background_group = pygame.sprite.Group()
background_group.add(Background(settings, settings.BACKGROUND_IMAGE, 0))
background_group.add(Background(settings, settings.BACKGROUND_IMAGE, 0 - settings.WINDOW_HEIGHT))
background_group.draw(window_surface)
ground_group = pygame.sprite.Group()
ground_group.add(Ground(settings.GROUND_IMAGE))
ground_group.draw(window_surface)
draw_text('Dodger', font, window_surface, settings.WINDOW_WIDTH // 3, settings.WINDOW_HEIGHT // 3)
draw_text('Press a key to start.', font, window_surface, settings.WINDOW_WIDTH // 3, (settings.WINDOW_HEIGHT // 3) + 50)
pygame.display.update()
wait_for_player_to_press_key()


# First game loop
while True:
    # Start a new game
    player = Player(settings.WINDOW_HEIGHT/2, settings.WINDOW_WIDTH/2)
    player_group = pygame.sprite.GroupSingle(player)
    baddie_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    player_group.draw(window_surface)
    score = 0
    baddie_add_counter = 0
    platform_add_counter = 0
    pygame.mixer.music.play(-1, 0.0)

    platform_group.add(MyPlatform(settings, score, settings.PLATFORM_IMAGE))
    

    # Second game loop
    while True:
        score += 1

        # Event handling
        for event in pygame.event.get():
            player.handle_input(event, ground_group, platform_group)

        # Add new baddies
        baddie_add_counter += 1
        if baddie_add_counter >= settings.ADD_NEW_BADDIE_RATE:
            baddie_add_counter = 0
            baddie_group.add(Baddies(settings, settings.BADDIE_IMAGE))

        # Add new platform 
        platform_add_counter += 1
        if platform_add_counter >= settings.ADD_NEW_PLATFORM_RATE:
            platform_add_counter = 0
            platform_group.add(Platform(settings, settings.PLATFORM_IMAGE))

        # Update game objects
        player.update(ground_group, platform_group)
        baddie_group.update()
        platform_group.update()
        background_group.update()

        # Draw everything
        background_group.draw(window_surface)
        draw_text('Score: %s' % (score), font, window_surface, 10, 0)
        player_group.draw(window_surface)
        baddie_group.draw(window_surface)
        platform_group.draw(window_surface)
        ground_group.draw(window_surface)



        # Update display inside the game
        pygame.display.update()
        
        # If the player touched a baddie he lost
        if pygame.sprite.spritecollide(player, baddie_group, False):
            break

        # Increment score and control FPS
        clock.tick(settings.FPS)
    
    # Shows the game over screen
    pygame.mixer.music.stop()
    game_over_sound.play()
    game_over_text(window_surface)
    pygame.display.update()
    wait_for_player_to_press_key()
    game_over_sound.stop()
