# main.py
import pygame
import sys
from settings import settings
from menu import MainMenu, OptionsMenu, PauseMenu
from game_loop import run_game_app 

pygame.init()

settings.resize(settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT)
screen, windowed_size = settings.create_window()

clock = pygame.time.Clock()
# C'est ici que la font est créée, on doit la faire voyager
font = pygame.font.SysFont(None, 48)

def rebuild_assets():
    settings.initialize_static_layers(pygame.display.get_surface())

rebuild_assets()

main_menu = MainMenu(font)
options_menu = OptionsMenu(font)
pause_menu = PauseMenu(font)

# On ajoute 'font=font' à la fin de l'appel
run_game_app(
    screen, 
    windowed_size, 
    settings, 
    main_menu, 
    options_menu, 
    pause_menu, 
    clock, 
    rebuild_static_layers=rebuild_assets,
    font=font  # <--- AJOUT CRUCIAL
)