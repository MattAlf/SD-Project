import sys
import pygame
from menu import show_main_menu
from game_loop import run_game_round
from settings import settings


def run_app(screen, main_menu, options_menu, pause_menu, game_over_menu, help_menu, clock, font):
    """
    Coordinates the main menu and gameplay loops.
    Returns when the process exits.
    """
    # Mutable holders so nested functions see updated refs
    screen_ref = [screen]

    while True:
        # Menu phase
        new_screen = show_main_menu(
            screen_ref[0],
            main_menu,
            options_menu,
            help_menu,
            clock
        )
        screen_ref[0] = new_screen

        # Gameplay phase (repeat until player returns to main menu)
        while True:
            result = run_game_round(
                screen_ref[0],
                pause_menu,
                game_over_menu,
                font,
                settings.GAME_OVER_SOUND
            )
            if result == "MAIN_MENU":
                break
