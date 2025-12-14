import os
import sys
import pygame
from pathlib import Path  # Used to locate asset files relative to this script.

# Creates the terminate() function that will close the game when needed.
def terminate():
    pygame.quit()
    sys.exit()
class Settings:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_DIMENSIONS = (WINDOW_WIDTH, WINDOW_HEIGHT) # We create a tuple to use the dimensions more easily.
    
    FPS = 60
    # BACKGROUND_SCROLL_SPEED_MULTIPLICATOR. It will speed up the background scrolling speed while keeping the
    # parallax effect in the same proportions. (To avoid bugs don't go below 0.6)
    BACKGROUND_SCROLL_SPEED_MULTIPLICATOR = 0.7

    # Ghost related values.
    GHOST_MIN_SIZE = 30
    GHOST_MAX_SIZE = 40
    GHOST_MIN_SPEED = 1
    GHOST_MAX_SPEED = 8
    GHOST_SPAWN_RATE = 20 # It will be a spawn rate based on the FPS. (so 1 ghost every 20 frames)
    
    # Platform related values.
    PLATFORM_HEIGHT = 30 # In pixels
    PLATFORM_WIDTH = 250 # In pixels
    PLATFORM_SPEED =  5 # In pixels
    PLATFROM_SPAWN_RATE = 40 # It will be a spawn rate based on the FPS. (so 1 platform every 40 frames)

    # Shield related values.
    SHIELD_DURATION_TIME = 5000 # In milliseconds.
    SHIELD_PICKUP_SPAWN_RATE_MIN = 10000 # In milliseconds.
    SHIELD_PICKUP_SPAWN_RATE_MAX = 20000 # In milliseconds.
    SHIELD_PICKUP_SCROLL_SPEED = 4 # In pixels.
    SHIELD_PICKUP_SIZE = 50 # In pixels

    # Player related values.
    PLAYER_HEIGHT = 200 # The number to change to manipulate the player's size.
    PLAYER_HITBOX_IMAGE_WIDTH_FACTOR = 0.17 # ~ 300 pixels wide (original image, the width of the knight without the spear) / 1800 pixels wide (original image, the whole image)
    PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR = 0.50 # ~ 500 pixels high (original image, the height of the knight) / 1000 pixels high (original image, the whole image)
    PLAYER_HITBOX_X_OFFSET_FACTOR = 0.42 # ~ 800 pixels horizontal distance (original image, from the left side of the image to the knight) / 1800 pixels wide (original image, the whole image)
    PLAYER_HITBOX_Y_OFFSET_FACTOR = 0.33 # ~ 300 pixels vertical distance (original image, from the bottom of the image to the knight) / 1000 pixels high (original image, the whole image)
    PLAYER_JUMP_STRENGTH = 20 # How high the player can jump.
    PLAYER_ANIMATION_SLOWER = 2 # The higher the number, the slower the player animation speed.
    PLAYER_INVULNERABILITY_TIME = 2000 # In milliseconds.

    PLAYER_STARTING_LIVES = 3 # Number of lives at the start of the game.
    PLAYER_LIVES_DISPLAY_SIZE = 40 # In pixels
    PLAYER_LIVES_MARGIN_X = 10 # In pixels, it's the space between the window sides and the heart image.
    PLAYER_LIVES_MARGIN_Y = 10 # In pixels, it's the space between the window sides and the heart image.
    PLAYER_LIVES_HEART_SPACING = 5 # In pixels, it's the space between the hearts' images.

    # Dragon related values.
    DRAGON_WIDTH = 200 # In pixels.
    DRAGON_HEIGHT = 200 # In pixels.
    DRAGON_ATTACK_COOLDOWN = 1000 # In milliseconds.
    FIREBALL_SIZE = 30 # In pixels.
    FIREBALL_SPEED = 5 # In pixels.

    # Ground related values.
    GROUND_HEIGHT = 60 # In pixels.
    GROUND_HITBOX_IMAGE_HEIGHT_FACTOR = 0.70 # 70 pixels high (original image, height of the ground) / 100 pixels (original image height)

    # Spear related values.
    SPEAR_WIDTH = 100 # In pixels.
    SPEAR_SPEED = 20 # In pixels.
    SPEAR_ATTACK_COOLDOWN = 500 # In milliseconds.

    # Kinematics related values.
    HORIZONTAL_ACCELERATION = 2 # How quickly the player speeds up.
    HORIZONTAL_FRICTION = 0.2 # Friction.
    VERTICAL_ACCELERATION = 1 # Gravity.

    def __init__(self):
        # This variable is used to remember if the window is in fullscreen or not when the toggle_fullscreen function is used.
        self.is_fullscreen = False

        self.assets_dir = Path(__file__).parent # It makes locating the files more safe. (avoiding wrong directory problems)
        
        # Loading the menu related images.
        self.MAIN_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/main_menu.png")
        self.PAUSED_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/paused_menu.png")
        self.HELP_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/help_menu.png")
        self.GAME_OVER_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/game_over_menu.png")
        self.OPTIONS_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/options_menu.png")
        self.STORY_MENU_IMAGE = pygame.image.load(self.assets_dir / "menu_images/story_menu.png")
        self.HELP_ICON = pygame.image.load(self.assets_dir / "menu_images/help_icon.png")
        self.FULLSCREEN_ICON = pygame.image.load(self.assets_dir / "menu_images/fullscreen_icon.png")

        # Loading the game related images.
        # Enemy related images.
        self.GHOST_IMAGE = pygame.image.load(self.assets_dir / "ghost.png")
        self.DRAGON_IMAGE = pygame.image.load(self.assets_dir / "dragon.png")
        self.FIREBALL_IMAGE = pygame.image.load(self.assets_dir / "fire_arrow.png")
        # Player related images.
        self.SPEAR_IMAGE = pygame.image.load(self.assets_dir / "spear.png")
        self.RED_HEART_IMAGE = pygame.image.load(self.assets_dir / "red_heart.png")
        self.BLUE_HEART_IMAGE = pygame.image.load(self.assets_dir / "blue_heart.png")
        self.SHIELD_EFFECT_IMAGE = pygame.image.load(self.assets_dir / "shield_effect.png")
        self.SHIELD_PICKUP_IMAGE = pygame.image.load(self.assets_dir / "shield_pickup.png")
        # Scenery related images.
        self.PLATFORM_IMAGE = pygame.image.load(self.assets_dir / "platform.png")
        self.GROUND_IMAGE = pygame.image.load(self.assets_dir / "ground.png")
        # Tuples of the background image layer associated wiht its scrolling speed. The images loop horizontally and make the effect of an infinite image.
        self.BACKGROUND_IMAGES_AND_SPEEDS = [
            (pygame.image.load(self.assets_dir / "background_layers/1_sky.png"), self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/2_clouds.png"), 2 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/3_mountain.png"), self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/4_clouds.png"), 3 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/5_ground.png"), 4 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/6_ground.png"), 7 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/7_ground.png"), 8 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR),
            (pygame.image.load(self.assets_dir / "background_layers/8_plant.png"), 8 * self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR)
        ]
        # The player is animated. So in order to store all of the different animations we created a dictionary.
        # Each key gives acces to the list with all of the images related to this action. We also had to flip the images
        # to have an animation whether the player is facing right or left.
        self.PLAYER_IMAGES = {
            'PLAYER_RUN_RIGHT': [],
            'PLAYER_RUN_LEFT': [],
            'PLAYER_ATTACK_RIGHT': [],
            'PLAYER_ATTACK_LEFT': [],
            'PLAYER_DIE_RIGHT': [],
            'PLAYER_DIE_LEFT': [],
            'PLAYER_HURT_RIGHT': [],
            'PLAYER_HURT_LEFT': [],
            'PLAYER_IDLE_RIGHT': [],
            'PLAYER_IDLE_LEFT': [],
            'PLAYER_JUMP_RIGHT': [],
            'PLAYER_JUMP_LEFT': []
        }
        for action in list(self.PLAYER_IMAGES.keys()):
            if 'RUN_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_run_images/Knight_01__RUN_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_RUN_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_RUN_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'ATTACK_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_attack_images/Knight_01__ATTACK_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_ATTACK_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_ATTACK_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'DIE_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_die_images/Knight_01__DIE_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_DIE_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_DIE_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'HURT_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_hurt_images/Knight_01__HURT_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_HURT_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_HURT_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'IDLE_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_idle_images/Knight_01__IDLE_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_IDLE_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_IDLE_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'JUMP_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(self.assets_dir / f"player_animations/player_jump_images/Knight_01__JUMP_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_JUMP_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_JUMP_LEFT'].append(pygame.transform.flip(img, True, False))

    def load_music_and_sounds(self):
        # Music and sound effects levels. They go from 0 (no sound) to 1 (max sound). We set the default values to 0.5.
        self.music_volume = 0.5
        self.sound_effects_volume = 0.5
        # Loading the sound effects and the background music.
        # The sound effects are stored in a dictionary like for the player animations.
        self.ALL_SOUND_EFFECTS = {
            'GAME_OVER_SOUND': pygame.mixer.Sound(self.assets_dir / "gameover.wav")
        }
        # Setting the sound effects volume level to self.sound_effects_volume for all soun effects.
        for sound in self.ALL_SOUND_EFFECTS.values():
            sound.set_volume(self.sound_effects_volume)
        # Loading the background music and setting it to self.music_volume volume level.
        pygame.mixer.music.load(self.assets_dir / "background.mid")
        pygame.mixer.music.set_volume(self.music_volume)

    def convert_and_scale_player_images(self):
        scaled = {}
        # Creates empty lists for each animation key and scale each frame.
        for key in self.PLAYER_IMAGES:
            scaled[key] = []
            frames = self.PLAYER_IMAGES[key]

            for img in frames:
                converted_img = img.convert_alpha()
                scale_factor = self.PLAYER_HEIGHT / converted_img.get_height()
                new_width = int(converted_img.get_width() * scale_factor)
                new_height = int(converted_img.get_height() * scale_factor)
                converted_and_scaled = pygame.transform.scale(converted_img, (new_width, new_height))
                scaled[key].append(converted_and_scaled)

        # Stores the result.
        self.PLAYER_IMAGES = scaled

        # Stores draw size for later.
        idle_frame = scaled["PLAYER_IDLE_RIGHT"][0]
        self.PLAYER_DRAW_WIDTH = idle_frame.get_width()
        self.PLAYER_DRAW_HEIGHT = idle_frame.get_height()

    def convert_background_images(self):
        converted_bg_img_and_speed = []

        for image, speed in self.BACKGROUND_IMAGES_AND_SPEEDS:
            converted_img = image.convert_alpha()
            converted_bg_img_and_speed.append((converted_img, speed))

        self.BACKGROUND_IMAGES_AND_SPEEDS = converted_bg_img_and_speed

    def create_window(self):
        """Create a resizable window using the current settings dimensions."""
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        try:
            screen = pygame.display.set_mode(
                self.WINDOW_DIMENSIONS,
                pygame.SCALED | pygame.DOUBLEBUF,
                vsync=1
            )
        except TypeError:
            # Older pygame versions may not support vsync kwarg; fall back quietly.
            screen = pygame.display.set_mode(
                self.WINDOW_DIMENSIONS,
                pygame.SCALED | pygame.DOUBLEBUF
            )
        self.convert_and_scale_surfaces(screen)
        self.load_music_and_sounds()

        return screen
    
    def convert_and_scale_surfaces(self, screen):
        """Convert all loaded surfaces after a display mode is set (required for convert_alpha)."""
        self.convert_and_scale_player_images()
        self.convert_background_images()
        # Menu related images.
        converted_main_menu = self.MAIN_MENU_IMAGE.convert_alpha()
        self.MAIN_MENU_IMAGE = pygame.transform.scale(converted_main_menu, self.WINDOW_DIMENSIONS)

        converted_paused_menu = self.PAUSED_MENU_IMAGE.convert_alpha()
        self.PAUSED_MENU_IMAGE = pygame.transform.scale(converted_paused_menu, self.WINDOW_DIMENSIONS)

        converted_help_menu = self.HELP_MENU_IMAGE.convert_alpha()
        self.HELP_MENU_IMAGE = pygame.transform.scale(converted_help_menu, self.WINDOW_DIMENSIONS)

        converted_game_over_menu = self.GAME_OVER_MENU_IMAGE.convert_alpha()
        self.GAME_OVER_MENU_IMAGE = pygame.transform.scale(converted_game_over_menu, self.WINDOW_DIMENSIONS)

        converted_options_menu = self.OPTIONS_MENU_IMAGE.convert_alpha()
        self.OPTIONS_MENU_IMAGE = pygame.transform.scale(converted_options_menu, self.WINDOW_DIMENSIONS)

        converted_story_menu = self.STORY_MENU_IMAGE.convert_alpha()
        self.STORY_MENU_IMAGE = pygame.transform.scale(converted_story_menu, self.WINDOW_DIMENSIONS)

        converted_help_icon = self.HELP_ICON.convert_alpha()
        self.HELP_ICON = pygame.transform.smoothscale(converted_help_icon, (50, 50))
        
        converted_fullscreen_icon = self.FULLSCREEN_ICON.convert_alpha()
        self.FULLSCREEN_ICON = pygame.transform.smoothscale(converted_fullscreen_icon, (50, 50))
        # Enemy related images.
        self.GHOST_IMAGE = self.GHOST_IMAGE.convert_alpha()
        self.DRAGON_IMAGE = self.DRAGON_IMAGE.convert_alpha()
        self.FIREBALL_IMAGE = self.FIREBALL_IMAGE.convert_alpha()
        # Player related images.
        self.SPEAR_IMAGE = self.SPEAR_IMAGE.convert_alpha()
        self.RED_HEART_IMAGE = self.RED_HEART_IMAGE.convert_alpha()
        self.BLUE_HEART_IMAGE = self.BLUE_HEART_IMAGE.convert_alpha()
        self.SHIELD_EFFECT_IMAGE = self.SHIELD_EFFECT_IMAGE.convert_alpha()
        self.SHIELD_PICKUP_IMAGE = self.SHIELD_PICKUP_IMAGE.convert_alpha()
        # Scenery related images.
        self.PLATFORM_IMAGE = self.PLATFORM_IMAGE.convert_alpha()
        self.GROUND_IMAGE = self.GROUND_IMAGE.convert_alpha()
        
    def draw_score(self, surface, font, score, x=10, y=0, color=(0, 0, 122)):
        """Render the score text to the given surface."""
        text_surface = font.render(f"Score: {score}", True, color)
        text_rect = text_surface.get_rect(topleft=(x, y))
        surface.blit(text_surface, text_rect)

    def draw_kill_counter(self, surface, font, kill_counter, x=10, y=30, color =(0,0,122)):
        text_surface = font.render(f"Kill: {kill_counter}", True, color)
        text_rect = text_surface.get_rect(topleft=(x, y))
        surface.blit(text_surface, text_rect)

    def draw_lives(self, surface, player):
        """Draw the player's remaining lives as hearts on the top-right of the screen."""
        if not hasattr(player, "lives"):
            return
        heart_image = self.BLUE_HEART_IMAGE if getattr(player, "has_shield", False) else self.RED_HEART_IMAGE
        for i in range(player.lives):
            left = (
                self.WINDOW_WIDTH
                - self.PLAYER_LIVES_MARGIN_X
                - (self.PLAYER_LIVES_DISPLAY_SIZE * (i + 1))
                - (self.PLAYER_LIVES_HEART_SPACING * i)
            )
            surface.blit(heart_image, (left, self.PLAYER_LIVES_MARGIN_Y))

    def initialize_static_layers(self, screen):
        """Build and draw static layers once at startup."""
        self.background_group, self.ground_group = self.build_static_layers()
        self.background_group.draw(screen)
        self.ground_group.draw(screen)
        return self.background_group, self.ground_group

    def build_static_layers(self):
        """Create background and ground sprite groups sized to the current window."""
        from entity import Background, Ground  # Local import to avoid circular dependency on load.

        background_group = pygame.sprite.Group()
        for image, scrolling_speed in self.BACKGROUND_IMAGES_AND_SPEEDS:
            # Two tiles per layer are enough for seamless horizontal scrolling.
            background_group.add(Background(image, scrolling_speed, 0, 0))
            background_group.add(Background(image, scrolling_speed, self.WINDOW_WIDTH, 0))

        ground_group = pygame.sprite.Group()  # Ground collision surface.
        ground_group.add(Ground())
        return background_group, ground_group

settings = Settings()
