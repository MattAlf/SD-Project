import sys
import pygame
from menu import show_main_menu
from game_loop import run_game_round


def run_app(settings, screen, windowed_size, main_menu, options_menu, pause_menu, game_over_menu, clock, font):
    """
    Coordinates the main menu and gameplay loops.
    Returns when the process exits.
    """
    # Mutable holders so nested functions see updated refs
    screen_ref = [screen]
    window_ref = [windowed_size]

    def rebuild_static_layers():
        """Rebuild background/ground to match the current window."""
        settings.rebuild_static_layers(screen_ref[0])

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
            clock,
            rebuild_static_layers
        )
        screen_ref[0], window_ref[0] = new_screen, new_window

        if menu_choice == "EXIT":
            pygame.quit()
            sys.exit()

        # Gameplay phase (repeat until player returns to main menu)
        while True:
            result = run_game_round(
                screen_ref[0],
                settings,
                pause_menu,
                game_over_menu,
                font,
                settings.GAME_OVER_SOUND
            )
            if result == "MAIN_MENU":
                break
            if result == "EXIT":
                pygame.quit()
                sys.exit()

    return screen_ref[0], window_ref[0]
