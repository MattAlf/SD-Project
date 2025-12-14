# game_loop.py
# Encapsulates the gameplay loop so main.py stays focused on wiring menus and state transitions.
import random
import pygame
from pygame.locals import *
from entity import *
from functions import terminate


def run_game_round(screen, settings, pause_menu, game_over_menu, font, game_over_sound, global_high_score):
    """Run a single game round; returns a next action when the player pauses or dies."""
    background_group, ground_group = settings.build_static_layers()  # Static scenery.

    # Core game state setup.
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    baddie_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    spear_group = pygame.sprite.Group()
    shield_pickup_group = pygame.sprite.Group()
    shield_effect_group = pygame.sprite.Group()
    dragon_group = pygame.sprite.Group()
    fireball_group = pygame.sprite.Group()
    score = 0
    high_score = global_high_score 
    kill_counter = 0
    Bullet.kill_count = 0
    baddie_add_counter = 0
    platform_add_counter = 0
    dragon_alive = False
    next_shield_spawn = pygame.time.get_ticks() + random.randint(
        settings.SHIELD_PICKUP_SPAWN_RATE_MIN,
        settings.SHIELD_PICKUP_SPAWN_RATE_MAX,
    )
    paused = False
    music_muted_for_pause = False
    pause_music_volume = pygame.mixer.music.get_volume()
    pause_menu.create_buttons()

    def pause_game():
        nonlocal paused, music_muted_for_pause, pause_music_volume
        paused = True
        pause_menu.create_buttons()
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

    try:
        pygame.mixer.music.load(settings.GAME_MUSIC_PATH)
    except pygame.error:
        try:
            pygame.mixer.music.load(settings.BACKGROUND_MUSIC_PATH)
        except pygame.error:
            pass
    pygame.mixer.music.set_volume(settings.music_volume)
    pygame.mixer.music.play(-1, 0.0)  # Loop background music for this round.

    fps_clock = pygame.time.Clock()
    fps_font = pygame.font.SysFont(None, 24)
    last_fps_blit = 0
    fps_text = None

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
                    terminate()

        if paused:
            pause_menu.draw(screen)
            pygame.display.update()
            fps_clock.tick(settings.FPS)
            continue

        score += 1  # Increment score every frame as a simple timer.

        # Spawn dragon when score reaches 1000
        if score%1000 == 0 and not dragon_alive:
            dragon_group.add(Dragon(player))
            dragon_alive = True

        # Add new baddies (only if dragon hasn't spawned).
        baddie_add_counter += 1
        if baddie_add_counter >= settings.ADD_NEW_BADDIE_RATE and not dragon_alive:
            baddie_add_counter = 0
            baddie_group.add(Baddies())

        # Add new platform at a fixed cadence.
        platform_add_counter += 1
        if platform_add_counter >= settings.ADD_NEW_PLATFORM_RATE:
            platform_add_counter = 0
            for i in range (random.randint(1,2)):
                platform_group.add(Platform())

        now_ticks = pygame.time.get_ticks()

        if now_ticks >= next_shield_spawn and not shield_pickup_group:
            shield_pickup_group.add(ShieldPickup())
            next_shield_spawn = now_ticks + random.randint(
                settings.SHIELD_PICKUP_SPAWN_RATE_MIN,
                settings.SHIELD_PICKUP_SPAWN_RATE_MAX,
            )

        # Update game objects.
        platform_group.update()
        player_group.update(events, ground_group, platform_group, spear_group, baddie_group, shield_pickup_group, shield_effect_group)
        baddie_group.update()
        spear_group.update(baddie_group)
        dragon_group.update(fireball_group, spear_group, score)
        fireball_group.update()
        background_group.update()
        shield_pickup_group.update()
        shield_effect_group.update()
        kill_counter = Bullet.kill_count
        
        # Check collisions: fireballs hitting the player
        hit_fireballs = pygame.sprite.spritecollide(player, fireball_group, True)
        for fireball in hit_fireballs:
            player.take_damage()
        
        # Check collisions: dragon hitting the player
        if pygame.sprite.spritecollide(player, dragon_group, False):
            player.take_damage()
            # Repousser le joueur
            if player.rect.centerx < settings.WINDOW_WIDTH // 2:
                player.position.x -= 20
            else:
                player.position.x += 20
        
        # Check if dragon is dead and respawn baddies
        if dragon_alive and len(dragon_group) == 0:
            dragon_alive = False

        # Draw everything.
        background_group.draw(screen)
        settings.draw_hud(screen, font, score, high_score, kill_counter, x=10, y=10)

        shield_pickup_group.draw(screen)
        screen.blit(player.image, player.full_image_rect)
        shield_effect_group.draw(screen)
        baddie_group.draw(screen)
        platform_group.draw(screen)
        spear_group.draw(screen)
        dragon_group.draw(screen)
        fireball_group.draw(screen)
        ground_group.draw(screen)
        settings.draw_lives(screen, player)

        # FPS overlay (updated once per 0.25s to avoid extra render cost).
        if now_ticks - last_fps_blit > 250:
            fps_text = fps_font.render(f"{int(fps_clock.get_fps())} FPS", True, (0, 0, 0))
            last_fps_blit = now_ticks
        if fps_text:
            screen.blit(fps_text, (10, 60))

        pygame.display.update()  # Present frame.

        if player.dead:
            final_score = score + 50 * kill_counter
            new_high_score = max(global_high_score, final_score)
            return new_high_score

        fps_clock.tick(settings.FPS)  # Control FPS inside game loop.

    # Show the game over screen with retry/main menu options.
    pygame.mixer.music.stop()
    game_over_sound.play()
    game_over_menu.create_buttons()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            action = game_over_menu.handle_event(event)
            if action == "RETRY":
                game_over_sound.stop()
                return "RETRY"
            if action == "MAIN_MENU":
                game_over_sound.stop()
                return "MAIN_MENU"
            if action == "EXIT":
                pygame.quit()
                raise SystemExit

        game_over_menu.draw(screen, score, kill_counter)
        pygame.display.update()
        fps_clock.tick(settings.FPS)
