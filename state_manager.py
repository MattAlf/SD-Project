import sys
import pygame
from menu import show_main_menu
from game_loop import run_game_round

def run_app(settings, screen, windowed_size, main_menu, options_menu, pause_menu, game_over_menu, help_menu, clock, font, global_high_score):
    """
    Coordinates the main menu and gameplay loops.
    Returns when the process exits.
    """
    # Mutable holders so nested functions see updated refs
    screen_ref = [screen]
    window_ref = [windowed_size]

    while True:
        # Menu phase
        menu_choice, new_screen, new_window = show_main_menu(
            screen_ref[0],
            window_ref[0],
            settings,
            main_menu,
            options_menu,
            pause_menu,
            game_over_menu,
            help_menu,
            clock
        )
        screen_ref[0], window_ref[0] = new_screen, new_window

        # Gameplay phase (repeat until player returns to main menu)
        while True:
            result = run_game_round(
                screen_ref[0],
                settings,
                pause_menu,
                game_over_menu,
                font,
                settings.GAME_OVER_SOUND,
                global_high_score
            )
            if result == "MAIN_MENU":
                break
            else:
                global_high_score = result
                with open("highscore.txt", "w") as f:
                    f.write(str(global_high_score))
