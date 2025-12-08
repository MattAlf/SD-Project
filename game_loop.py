# game_loop.py
# Encapsulates the gameplay loop so main.py stays focused on wiring menus and state transitions.
import pygame
from pygame.locals import *
from entity import Player, Platform  # Baddies available if spawn is re-enabled.
from functions import game_over_text, wait_for_player_to_press_key


def run_game_round(screen, settings, pause_menu, font, game_over_sound):
    """Run a single game round; returns when the player dies or exits to main menu."""
    background_group, ground_group = settings.build_static_layers()  # Static scenery.

    # Core game state setup.
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    baddie_group = pygame.sprite.Group()  # Enemies (spawn disabled but scaffold kept).
    platform_group = pygame.sprite.Group()
    spear_group = pygame.sprite.Group()
    score = 0
    baddie_add_counter = 0
    platform_add_counter = 0
    paused = False
    music_muted_for_pause = False
    pause_music_volume = pygame.mixer.music.get_volume()
    pause_menu._create_buttons()
    clock = pygame.time.Clock()  # Single clock reused for FPS throttling.

    def pause_game():
        nonlocal paused, music_muted_for_pause, pause_music_volume
        paused = True
        pause_menu._create_buttons()
        pause_music_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.pause()
        pygame.mixer.music.set_volume(0.0)
        music_muted_for_pause = True

    def resume_game():
        nonlocal paused, music_muted_for_pause
        paused = False
        if music_muted_for_pause:
            pygame.mixer.music.unpause()
            pygame.mixer.music.set_volume(pause_music_volume)
            music_muted_for_pause = False

    pygame.mixer.music.play(-1, 0.0)  # Loop background music for this round.

    while True:
        events = pygame.event.get()  # Capture all events for this frame.

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if paused:
                    resume_game()
                else:
                    pause_game()
                continue

            if paused:
                action = pause_menu.handle_event(event)  # Handle pause menu buttons.
                if action == "RESUME":
                    resume_game()
                elif action == "MAIN_MENU":
                    if music_muted_for_pause:
                        pygame.mixer.music.set_volume(pause_music_volume)
                    pygame.mixer.music.stop()
                    return "MAIN_MENU"
                elif action == "EXIT":
                    pygame.quit()
                    raise SystemExit

        if paused:
            pause_menu.draw(screen)
            pygame.display.update()
            clock.tick(settings.FPS)
            continue

        score += 1  # Increment score every frame as a simple timer.

        # Add new baddies (currently disabled; keep counter for future use).
        baddie_add_counter += 1
        if baddie_add_counter >= settings.ADD_NEW_BADDIE_RATE:
            baddie_add_counter = 0
 #           baddie_group.add(Baddies())

        # Add new platform at a fixed cadence.
        platform_add_counter += 1
        if platform_add_counter >= settings.ADD_NEW_PLATFORM_RATE:
            platform_add_counter = 0
            platform_group.add(Platform())

        # Update game objects.
        platform_group.update()
        player_group.update(events, ground_group, platform_group, spear_group)
        baddie_group.update()
        spear_group.update()
        background_group.update()

        # Draw everything.
        background_group.draw(screen)
        settings.draw_score(screen, font, score)
        screen.blit(player.image, player.full_image_rect)
        baddie_group.draw(screen)
        platform_group.draw(screen)
        spear_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()  # Present frame.

        # If the player touched a baddie he lost.
        if pygame.sprite.spritecollide(player, baddie_group, False):
            break

        clock.tick(settings.FPS)  # Control FPS inside game loop.

    # Shows the game over screen.
    pygame.mixer.music.stop()
    game_over_sound.play()
    game_over_text(screen)
    pygame.display.update()
    wait_for_player_to_press_key()
    game_over_sound.stop()
    return "GAME_OVER"


def run_game_app(screen, windowed_size, settings, main_menu, options_menu, pause_menu, clock, rebuild_static_layers, run_game_round_fn):
    """Outer game loop: menu → game round → repeat. Updates screen/window on fullscreen toggle."""
    from menu import show_main_menu
    while True:
        menu_choice, screen, windowed_size = show_main_menu(
            screen,
            windowed_size,
            settings,
            main_menu,
            options_menu,
            pause_menu,
            clock,
            rebuild_static_layers
        )
        if menu_choice == "EXIT":
            import pygame, sys
            pygame.quit()
            sys.exit()

        while True:
            round_result = run_game_round_fn()
            if round_result == "MAIN_MENU":
                break

    return screen, windowed_size
