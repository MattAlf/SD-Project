# game_loop.py
# Encapsulates the gameplay loop so main.py stays focused on wiring menus and state transitions.
import random
import pygame
from pygame.locals import *
from entity import Player, Spear, ShieldPickup, ShieldEffect, Dragon, Fireball, Ghosts, Platform, Ground, Background
from settings import settings, terminate


def run_game_round(screen, pause_menu, game_over_menu, font):
    '''Run a single game round; returns a next action when the player pauses or dies.'''
    pygame.mixer.music.load(settings.assets_dir / 'musics/in_game_music.wav')
    background_group, ground_group = settings.initialize_static_layers(screen)  # Static scenery.

    # Core game state setup.
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    spear_group = pygame.sprite.Group()

    ghost_group = pygame.sprite.Group()
    dragon_group = pygame.sprite.Group()
    fireball_group = pygame.sprite.Group()

    platform_group = pygame.sprite.Group()
    shield_pickup_group = pygame.sprite.Group()
    shield_effect_group = pygame.sprite.Group()

    score = 0
    kill_counter = 0
    Spear.kill_count = 0

    ghost_add_counter = 0
    platform_add_counter = 0

    dragon_alive = False
    next_shield_spawn = pygame.time.get_ticks() + random.randint(
        settings.SHIELD_PICKUP_SPAWN_RATE_MIN,
        settings.SHIELD_PICKUP_SPAWN_RATE_MAX,
    )
    paused = False

    def pause_game():
        nonlocal paused
        paused = True
        pause_menu.create_buttons()
        pygame.mixer.music.pause()

    def resume_game():
        nonlocal paused
        paused = False
        pygame.mixer.music.unpause()

    pygame.mixer.music.play(-1, 0.0)  # Loop background music for this round.
    clock = pygame.time.Clock()                
    while True:
        events = pygame.event.get()  # Capture all events for this frame.
        for event in events:
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if paused:
                    resume_game()
                else:
                    pause_game()
        if paused:
            for event in events:
                result = pause_menu.handle_event(event)  # Handle pause menu buttons.
                if result == 'RESUME':
                    resume_game()
                elif result == 'MAIN_MENU':
                    return 'MAIN_MENU'
                elif result == 'EXIT':
                    terminate()
            pause_menu.draw(screen)
            pygame.display.update()
            clock.tick(settings.FPS)
            continue
        for event in events:
            if event.type == KEYDOWN:
                if event.key in (K_UP, K_w) and (player.on_ground or player.on_platform):
                    player.jump(ground_group, platform_group)
                    settings.ALL_SOUND_EFFECTS['PLAYER_JUMP'].play()
                if event.key in (K_SPACE, K_RETURN, K_KP_ENTER) and (not player.attack_left and not player.attack_right):
                    player.attack(spear_group)
                if event.key == K_DOWN:
                    player.drop_through = True
            if event.type == KEYUP and event.key == K_DOWN:
                player.drop_through = False
                
        # Here we look at the state of the all the keys at each frame. It is useful because
        # running left or right are continuous movements.
        keys = pygame.key.get_pressed()
        player.run_left = keys[K_LEFT] or keys[K_a]
        player.run_right = keys[K_RIGHT] or keys[K_d]
        if player.run_left and player.run_right:
            player.run_left = player.run_right = False

        score += 1  # Increment score every frame as a simple timer.
        current_time = pygame.time.get_ticks()

        # Spawn dragon when score reaches 2000
        if score % 2000 == 0 and not dragon_alive:
            dragon_group.add(Dragon(player))
            dragon_alive = True

        # Add new ghosts (only if dragon hasn't spawned).
        ghost_add_counter += 1
        if ghost_add_counter >= settings.GHOST_SPAWN_RATE and not dragon_alive:
            ghost_add_counter = 0
            ghost_group.add(Ghosts())

        # Add new platform at a fixed cadence.
        platform_add_counter += 1
        if platform_add_counter >= settings.PLATFROM_SPAWN_RATE:
            platform_add_counter = 0
            platform_group.add(Platform())

        if current_time >= next_shield_spawn and not shield_pickup_group:
            shield_pickup_group.add(ShieldPickup())
            next_shield_spawn = current_time + random.randint(
                settings.SHIELD_PICKUP_SPAWN_RATE_MIN,
                settings.SHIELD_PICKUP_SPAWN_RATE_MAX,
            )

        # Update game objects.
        player_group.update(current_time, ground_group, platform_group)
        platform_group.update()
        ghost_group.update()
        spear_group.update(ghost_group)
        dragon_group.update(current_time, fireball_group, spear_group, score)
        fireball_group.update()
        background_group.update()
        ground_group.update()
        shield_pickup_group.update()
        shield_effect_group.update()
        kill_counter = Spear.kill_count

        player.check_for_enemy_collision(ghost_group, fireball_group, dragon_group)
        player.check_for_pickable_objects_collision(shield_pickup_group, shield_effect_group)
                
        # Check if dragon is dead and respawn ghosts
        if dragon_alive and len(dragon_group) == 0:
            dragon_alive = False

        # Draw everything.
        background_group.draw(screen)

        screen.blit(player.image, player.full_image_rect)
        shield_effect_group.draw(screen)

        platform_group.draw(screen)
        ghost_group.draw(screen)
        shield_pickup_group.draw(screen)
        spear_group.draw(screen)
        dragon_group.draw(screen)
        fireball_group.draw(screen)

        for ground in ground_group:
            screen.blit(ground.image, ground.full_image_rect)
        settings.draw_hud(screen, font, score, kill_counter)
        settings.draw_lives(screen, player)

        pygame.display.update()  # Present frame.

        if player.dead:
            settings.ALL_SOUND_EFFECTS['PLAYER_DEATH'].play()
            settings.ALL_SOUND_EFFECTS['GAME_OVER'].play()
            score += 50 * kill_counter
            settings.highest_score = max(score, settings.highest_score)
            break

        clock.tick(settings.FPS)  # Control FPS inside game loop.

    # Show the game over screen with retry/main menu options.
    pygame.mixer.music.stop()
    settings.ALL_SOUND_EFFECTS['GAME_OVER'].play()
    game_over_menu.create_buttons()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            action = game_over_menu.handle_event(event)
            if action == 'RETRY':
                settings.ALL_SOUND_EFFECTS['GAME_OVER'].stop()
                return 'RETRY'
            if action == 'MAIN_MENU':
                settings.ALL_SOUND_EFFECTS['GAME_OVER'].stop()
                return 'MAIN_MENU'
            if action == 'EXIT':
                terminate()

        game_over_menu.draw(screen, score, kill_counter)
        pygame.display.update()
        clock.tick(settings.FPS)
