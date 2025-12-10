# game_loop.py
import pygame
from pygame.locals import *
from entity import Player, Platform, Baddies  # Ajout de Baddies
from functions import game_over_text, wait_for_player_to_press_key
import menu

def run_game_round(screen, windowed_size, settings, main_menu, options_menu, pause_menu, clock, font):
    """
    Exécute un round de jeu.
    Note l'ajout de l'argument 'font' à la fin.
    """
    
    background_group = None
    ground_group = None
    
    def refresh_game_scenery():
        nonlocal background_group, ground_group
        background_group, ground_group = settings.build_static_layers()

    refresh_game_scenery()

    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    baddie_group = pygame.sprite.Group() 
    platform_group = pygame.sprite.Group()
    spear_group = pygame.sprite.Group()
    
    score = 0
    baddie_add_counter = 0
    platform_add_counter = 0

    pygame.mixer.music.play(-1, 0.0)

    fps_font = pygame.font.SysFont(None, 24)
    last_fps_blit = 0
    fps_text = None

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.mixer.music.pause()
                action, screen, windowed_size = menu.run_menu_loop(
                    screen, windowed_size, main_menu, options_menu, pause_menu, 
                    clock, start_in_pause=True, rebuild_static_layers=refresh_game_scenery
                )

                if action == "MAIN_MENU":
                    pygame.mixer.music.stop()
                    return "MAIN_MENU", screen, windowed_size
                elif action == "RESUME":
                    pygame.mixer.music.unpause()

        score += 1 

        # --- SPAWN DES ENNEMIS (Corrigé) ---
        baddie_add_counter += 1
        if baddie_add_counter >= settings.ADD_NEW_BADDIE_RATE:
            baddie_add_counter = 0
            baddie_group.add(Baddies())

        # --- SPAWN DES PLATEFORMES ---
        platform_add_counter += 1
        if platform_add_counter >= settings.ADD_NEW_PLATFORM_RATE:
            platform_add_counter = 0
            platform_group.add(Platform())

        # Updates
        platform_group.update()
        player_group.update(events, ground_group, platform_group, spear_group)
        baddie_group.update()
        spear_group.update()
        background_group.update()

        # Dessin
        background_group.draw(screen)
        
        # CORRECTION ICI : on passe la variable 'font' reçue en argument
        settings.draw_score(screen, font, score) 
        
        screen.blit(player.image, player.full_image_rect)
        baddie_group.draw(screen)
        platform_group.draw(screen)
        spear_group.draw(screen)
        ground_group.draw(screen)

        # FPS
        now_ticks = pygame.time.get_ticks()
        if now_ticks - last_fps_blit > 250:
            fps_text = fps_font.render(f"{int(clock.get_fps())} FPS", True, (0, 0, 0))
            last_fps_blit = now_ticks
        if fps_text:
            screen.blit(fps_text, (10, 30))

        pygame.display.update()

        if pygame.sprite.spritecollide(player, baddie_group, False):
            break

        clock.tick(settings.FPS)

    pygame.mixer.music.stop()
    settings.GAME_OVER_SOUND.play() # Utilisation du son chargé dans settings
    
    game_over_text(screen)
    pygame.display.update()
    wait_for_player_to_press_key()
    
    return "GAME_OVER", screen, windowed_size


def run_game_app(screen, windowed_size, settings, main_menu, options_menu, pause_menu, clock, rebuild_static_layers, font):
    """
    Boucle principale.
    Note l'ajout de l'argument 'font' à la fin.
    """
    while True:
        menu_choice, screen, windowed_size = menu.run_menu_loop(
            screen,
            windowed_size,
            main_menu,
            options_menu,
            pause_menu,
            clock,
            start_in_pause=False,
            rebuild_static_layers=rebuild_static_layers
        )

        if menu_choice == "START":
            while True:
                # On passe 'font' à run_game_round
                result, screen, windowed_size = run_game_round(
                    screen, windowed_size, settings, main_menu, options_menu, pause_menu, clock, font
                )
                
                if result == "MAIN_MENU":
                    break 
                
                if result == "GAME_OVER":
                    break 

    return screen, windowed_size