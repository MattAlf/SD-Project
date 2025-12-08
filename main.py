# main.py
import pygame
import sys
from pygame.locals import *
from settings import settings
from menu import MainMenu, OptionsMenu, PauseMenu
from state_manager import run_app



pygame.init()

info = pygame.display.Info()  # Grab current display info
settings.resize(settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT)  # Apply windowed size to all scalable settings

# Create the window and remember windowed size for toggling fullscreen
screen, windowed_size = settings.create_window()

clock = pygame.time.Clock()  # Regulates FPS across menus and gameplay.
font = pygame.font.SysFont(None, 48)  # Shared font for UI text.

# Build static layers sized to the current screen.
settings.initialize_static_layers(screen)

main_menu = MainMenu(settings, font)  # Main menu UI.
options_menu = OptionsMenu(settings, font)  # Options UI (fullscreen + volume).
pause_menu = PauseMenu(font)  # Pause overlay UI.

# Delegate outer loop to state manager
run_app(settings, screen, windowed_size, main_menu, options_menu, pause_menu, clock, font)
