from menu import run_main_menu
from game_loop import run_game_round

def run_app(screen, main_menu, options_menu, pause_menu, game_over_menu, help_menu, story_menu, clock, font):
    '''
    Coordinates the main menu and gameplay loops.
    Returns when the process exits.
    '''
    # Mutable holders so nested functions see updated refs

    while True:
        # Menu phase
        run_main_menu(
            screen,
            main_menu,
            options_menu,
            help_menu,
            story_menu,
            clock
        )

        # Gameplay phase (repeat until player returns to main menu)
        while True:
            result = run_game_round(
                screen,
                pause_menu,
                game_over_menu,
                font
            )
            if result == 'MAIN_MENU':
                break
            if result == 'RETRY':
                continue
