# functions.py
import pygame
import sys
from pygame.locals import *
from settings import Settings

settings = Settings()

def draw_text(text, font, surface, x, y, color=(0, 0, 122)):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# Quit Pygame and exit the program.
def terminate():
    pygame.quit()
    sys.exit()

# Pause the game until the player presses a key.
def wait_for_player_to_press_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return
def game_over_text(surface):
    font_game_over = pygame.font.Font(None, 48)
    text_game_over = font_game_over.render('GAME OVER', True, settings.TEXT_COLOR)
    text_rect_game_over = text_game_over.get_rect()
    text_rect_game_over.center = (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 3)
    surface.blit(text_game_over, text_rect_game_over)

    font_game_over_subtitle = pygame.font.Font(None, 48)
    text_game_over_subtitle = font_game_over.render('Press a key to play again.', True, settings.TEXT_COLOR)
    text_rect_game_over_subtitle = text_game_over_subtitle.get_rect()
    text_rect_game_over_subtitle.center = (settings.WINDOW_WIDTH // 2, (settings.WINDOW_HEIGHT // 3) + 30)
    surface.blit(text_game_over_subtitle, text_rect_game_over_subtitle)    
