# main.py
import pygame
from pygame.locals import *
from settings import settings
from menu import MainMenu, OptionsMenu, PauseMenu, GameOverMenu, HelpMenu
from state_manager import run_app



pygame.init()

settings.resize(settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT)  # Apply windowed size to all scalable settings

# Create the window and remember windowed size for toggling fullscreen
screen = settings.create_window()

clock = pygame.time.Clock()  # Regulates FPS across menus and gameplay.
font = pygame.font.SysFont(None, 48)  # Shared font for UI text.

# Build static layers sized to the current screen.
settings.initialize_static_layers(screen)

main_menu = MainMenu(font)  # Main menu UI.
options_menu = OptionsMenu(font)  # Options UI (fullscreen + volume).
pause_menu = PauseMenu(font)  # Pause overlay UI.
game_over_menu = GameOverMenu(font)  # Game over UI.
help_menu = HelpMenu(font)

# Delegate outer loop to state manager
run_app(screen, main_menu, options_menu, pause_menu, game_over_menu, help_menu, clock, font)
