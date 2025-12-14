# main.py
import pygame
from pygame.locals import *
from settings import settings
from menu import MainMenu, OptionsMenu, PauseMenu, GameOverMenu, HelpMenu, StoryMenu
from state_manager import run_app


pygame.init()

# Create the window and remember windowed size for toggling fullscreen
screen = settings.create_window()

clock = pygame.time.Clock()  # Regulates FPS across menus and gameplay.
font = pygame.font.SysFont(None, 48)  # Shared font for UI text.

main_menu = MainMenu(font)  # Main menu UI.
options_menu = OptionsMenu(font)  # Options UI (fullscreen + volume).
pause_menu = PauseMenu(font)  # Pause overlay UI.
game_over_menu = GameOverMenu(font)  # Game over UI.
help_menu = HelpMenu(font)
story_menu = StoryMenu(font)

# Delegate outer loop to state manager
run_app(screen, main_menu, options_menu, pause_menu, game_over_menu, help_menu, story_menu, clock, font)
