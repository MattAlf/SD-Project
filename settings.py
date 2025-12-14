import os
import pygame
from pathlib import Path  # Used to locate asset files relative to this script.


class Settings:
    """Stores tunable values and scales them to the current screen size."""

    DEFAULT_WINDOW_WIDTH = 1280  # Default windowed width.
    DEFAULT_WINDOW_HEIGHT = 720  # Default windowed height.

    def __init__(self):
        if not pygame.get_init():
            pygame.init()  # Ensure pygame is ready before loading assets.

        self.FPS = 60  # Target frames per second.
        self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR = 0.7  # Parallax base speed.

        assets_dir = Path(__file__).parent  # Folder containing assets.
        # Load raw; we'll convert after a display mode is set.
        # Menu related images
        self.MAIN_MENU_IMAGE = pygame.image.load(assets_dir / "assets/main_menu.png")
        self.PAUSED_MENU_IMAGE = pygame.image.load(assets_dir / "assets/pause_menu.png")
        self.HELP_MENU_IMAGE = pygame.image.load(assets_dir / "assets/help_menu.png")
        self.HELP_ICON = pygame.image.load(assets_dir / "assets/help_icon.png")
        self.HELP_ICON = pygame.transform.smoothscale(self.HELP_ICON, (24, 24))



        # Game related images
        self.SPEAR_IMAGE = pygame.image.load(assets_dir / "assets/spear.png")
        self.BADDIE_IMAGE = pygame.image.load(assets_dir / "assets/baddie.png")
        self.PLATFORM_IMAGE = pygame.image.load(assets_dir / "assets/platform.png")
        self.GROUND_IMAGE = pygame.image.load(assets_dir / "background_layers/ground.png")
        self.GRASS_IMAGE = pygame.image.load(assets_dir / "background_layers/grass.png")
        self.RED_HEART_IMAGE = pygame.image.load(assets_dir / "assets/red_heart.png")
        self.BLUE_HEART_IMAGE = pygame.image.load(assets_dir / "assets/blue_heart.png")
        self.SHIELD_EFFECT_IMAGE = pygame.image.load(assets_dir / "assets/shield_effect.png")
        self.SHIELD_PICKUP_IMAGE = pygame.image.load(assets_dir / "assets/shield_pickup.png")
        self.DRAGON_IMAGE = pygame.image.load(assets_dir / "assets/dragon.png")
        self.FIREBALL_IMAGE = pygame.image.load(assets_dir / "assets/fire_arrow.png")
        self.WOOD_PANEL_IMAGE = pygame.image.load(assets_dir / "assets/wood_panel.png")
        self.BACKGROUND_LAYERS = [
            pygame.image.load(assets_dir / "background_layers/1_sky.png"),
            pygame.image.load(assets_dir / "background_layers/2_clouds.png"),
            pygame.image.load(assets_dir / "background_layers/3_mountain.png"),
            pygame.image.load(assets_dir / "background_layers/4_clouds.png"),
            pygame.image.load(assets_dir / "background_layers/5_ground.png"),
            pygame.image.load(assets_dir / "background_layers/6_ground.png"),
            pygame.image.load(assets_dir / "background_layers/7_ground.png"),
            pygame.image.load(assets_dir / "background_layers/8_plant.png"),
        ]

        # Music and sound effects
        self.music_volume = 0.5
        self.sound_effects_volume = 0.5

        self.GAME_OVER_SOUND = pygame.mixer.Sound(assets_dir / "gameover.wav")
        self.ALL_SOUND_EFFECTS = [self.GAME_OVER_SOUND]  # filled later with your sounds

        for sound in self.ALL_SOUND_EFFECTS:
            sound.set_volume(self.sound_effects_volume)

        self.BACKGROUND_MUSIC_PATH = assets_dir / "background.mid"
        pygame.mixer.music.load(self.BACKGROUND_MUSIC_PATH)



        # Preload the animated player sprites for reuse.
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
                    img = pygame.image.load(assets_dir / f"player_animations/player_run_images/Knight_01__RUN_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_RUN_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_RUN_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'ATTACK_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(assets_dir / f"player_animations/player_attack_images/Knight_01__ATTACK_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_ATTACK_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_ATTACK_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'DIE_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(assets_dir / f"player_animations/player_die_images/Knight_01__DIE_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_DIE_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_DIE_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'HURT_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(assets_dir / f"player_animations/player_hurt_images/Knight_01__HURT_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_HURT_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_HURT_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'IDLE_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(assets_dir / f"player_animations/player_idle_images/Knight_01__IDLE_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_IDLE_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_IDLE_LEFT'].append(pygame.transform.flip(img, True, False))
            elif 'JUMP_RIGHT' in action:
                for i in range(10):
                    img = pygame.image.load(assets_dir / f"player_animations/player_jump_images/Knight_01__JUMP_00{i}.png")
                    self.PLAYER_IMAGES['PLAYER_JUMP_RIGHT'].append(img)
                    self.PLAYER_IMAGES['PLAYER_JUMP_LEFT'].append(pygame.transform.flip(img, True, False))

        # Placeholder for scaled frames (filled in resize).
        self.PLAYER_SCALED_IMAGES = None
        self.PLAYER_DRAW_WIDTH = None
        self.PLAYER_DRAW_HEIGHT = None
        self._surfaces_converted = False

        # Cached static layers (background/ground).
        self.background_group = None
        self.ground_group = None

        self._base_baddie_rate = 20  # Base spawn cadence for enemies.
        self._base_platform_rate = 40  # Base spawn cadence for platforms.
        self.PLAYER_STARTING_LIVES = 3
        self.PLAYER_INVULNERABILITY_TIME = 2000  # ms
        self.SHIELD_DURATION_TIME = 5000  # ms
        self.SHIELD_PICKUP_SPAWN_RATE_MIN = 10000
        self.SHIELD_PICKUP_SPAWN_RATE_MAX = 20000
        self.SHIELD_PICKUP_SCROLL_SPEED_BASE = 4
        self.SHIELD_PICKUP_SIZE_BASE = 50
        self.PLAYER_LIVES_DISPLAY_SIZE_BASE = 40
        self.PLAYER_LIVES_MARGIN_X_BASE = 10
        self.PLAYER_LIVES_MARGIN_Y_BASE = 10
        self.PLAYER_LIVES_HEART_SPACING_BASE = 5
        self.DRAGON_WIDTH_BASE = 200
        self.DRAGON_HEIGHT_BASE = 200
        self.DRAGON_ATTACK_COOLDOWN = 1000  # ms
        self.FIREBALL_SIZE_BASE = 30
        self.FIREBALL_SPEED_BASE = 5
        
        # Initialize with the base size; the game will call resize with the actual display size.
        self.resize(self.DEFAULT_WINDOW_WIDTH, self.DEFAULT_WINDOW_HEIGHT)

    def resize(self, width: int, height: int):
        self.WINDOW_WIDTH = int(width)  # Actual window width in pixels.
        self.WINDOW_HEIGHT = int(height)  # Actual window height in pixels.

        scale_x = self.WINDOW_WIDTH / self.DEFAULT_WINDOW_WIDTH  # Horizontal scale ratio.
        scale_y = self.WINDOW_HEIGHT / self.DEFAULT_WINDOW_HEIGHT  # Vertical scale ratio.
        self.SCALE = min(scale_x, scale_y)  # Use the limiting scale to preserve aspect.
        s = self.SCALE  # Convenience alias.

        # World sizing (scaled by s with minimums to keep things visible).
        self.GROUND_HEIGHT = max(8, int(10 * s))
        self.PLATFORM_HEIGHT = max(30, int(30 * s))
        self.PLATFORM_WIDTH = max(90, int(200 * s))
        self.PLATFORM_SPEED = max(2, int(5 * s))

        self.PLAYER_HEIGHT = max(80, int(200 * s))
        self.PLAYER_HITBOX_IMAGE_WIDTH_FACTOR = 0.17
        self.PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR = 0.50
        self.PLAYER_HITBOX_X_OFFSET_FACTOR = 0.42
        self.PLAYER_HITBOX_Y_OFFSET_FACTOR = 0.33
        self.PLAYER_JUMP_STRENGTH = max(12.0, 20 * s)
        self.PLAYER_ANIMATION_SLOWER = 2
        self.SPEAR_WIDTH = max(40, int(100 * s))
        self.SPEAR_SPEED = max(8, int(20 * s))
        self.SPEAR_ATTACK_COOLDOWN = 500
        self.HORIZONTAL_ACCELERATION = 2 * s
        self.HORIZONTAL_FRICTION = 0.2 * s
        self.VERTICAL_ACCELERATION = max(0.5, 1 * s)
        self._build_scaled_player_images(self.PLAYER_HEIGHT)

        self.BADDIE_MIN_SIZE = max(40, int(60 * s))
        self.BADDIE_MAX_SIZE = max(self.BADDIE_MIN_SIZE, int(80 * s))
        self.BADDIE_MIN_SPEED = max(5, int(5 * s))
        self.BADDIE_MAX_SPEED = max(self.PLATFORM_SPEED + 10, self.PLATFORM_SPEED)

        self.SHIELD_PICKUP_SIZE = max(20, int(self.SHIELD_PICKUP_SIZE_BASE * s))
        self.SHIELD_PICKUP_SCROLL_SPEED = max(2, int(self.SHIELD_PICKUP_SCROLL_SPEED_BASE * s))
        self.PLAYER_LIVES_DISPLAY_SIZE = max(16, int(self.PLAYER_LIVES_DISPLAY_SIZE_BASE * s))
        self.PLAYER_LIVES_MARGIN_X = max(6, int(self.PLAYER_LIVES_MARGIN_X_BASE * s))
        self.PLAYER_LIVES_MARGIN_Y = max(6, int(self.PLAYER_LIVES_MARGIN_Y_BASE * s))
        self.PLAYER_LIVES_HEART_SPACING = max(2, int(self.PLAYER_LIVES_HEART_SPACING_BASE * s))
        self.DRAGON_WIDTH = max(100, int(self.DRAGON_WIDTH_BASE * s))
        self.DRAGON_HEIGHT = max(100, int(self.DRAGON_HEIGHT_BASE * s))
        self.FIREBALL_SIZE = max(15, int(self.FIREBALL_SIZE_BASE * s))
        self.FIREBALL_SPEED = max(3, int(self.FIREBALL_SPEED_BASE * s))

        self.BACKGROUND_SCROLL_SPEED = max(1, int(1 * s))
        base_bg_speed = max(1, int(self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR * max(1, s)))
        self.BACKGROUND_IMAGES_AND_SPEEDS = [
            (self.BACKGROUND_LAYERS[0], base_bg_speed),
            (self.BACKGROUND_LAYERS[1], 2 * base_bg_speed),
            (self.BACKGROUND_LAYERS[2], base_bg_speed),
            (self.BACKGROUND_LAYERS[3], 3 * base_bg_speed),
            (self.BACKGROUND_LAYERS[4], 3 * base_bg_speed),
            (self.BACKGROUND_LAYERS[5], 5 * base_bg_speed),
            (self.BACKGROUND_LAYERS[6], 8 * base_bg_speed),
            (self.BACKGROUND_LAYERS[7], 8 * base_bg_speed),
        ]
        self.GRASS_IMAGE_AND_SPEED = (self.GRASS_IMAGE, 10 * base_bg_speed)

        # Spawn cadence (higher scale → allow a few more entities on screen).
        self.ADD_NEW_BADDIE_RATE = max(6, int(self._base_baddie_rate / max(0.5, s)))
        self.ADD_NEW_PLATFORM_RATE = max(12, int(self._base_platform_rate / max(0.5, s)))
        self._scale_ui_surfaces()

    def build_static_layers(self):
        """Create background and ground sprite groups sized to the current window."""
        from entity import Background, Ground  # Local import to avoid circular dependency on load.

        bg_group = pygame.sprite.Group()
        for image, scrolling_speed in self.BACKGROUND_IMAGES_AND_SPEEDS:
            # Two tiles per layer are enough for seamless horizontal scrolling.
            bg_group.add(Background(image, scrolling_speed, 0, 0))
            bg_group.add(Background(image, scrolling_speed, self.WINDOW_WIDTH, 0))

        grd_group = pygame.sprite.Group()  # Ground collision surface.
        grd_group.add(Ground())
        return bg_group, grd_group

    def _build_scaled_player_images(self, target_height: int):
        """Pre-scale all player frames to the current target height to avoid per-frame scaling."""
        scaled = {key: [] for key in self.PLAYER_IMAGES.keys()}
        for key, frames in self.PLAYER_IMAGES.items():
            for img in frames:
                scale_factor = target_height / img.get_height()
                new_width = int(img.get_width() * scale_factor)
                new_height = int(img.get_height() * scale_factor)
                scaled[key].append(pygame.transform.scale(img, (new_width, new_height)))

        self.PLAYER_SCALED_IMAGES = scaled
        idle_frame = scaled['PLAYER_IDLE_RIGHT'][0]
        self.PLAYER_DRAW_WIDTH = idle_frame.get_width()
        self.PLAYER_DRAW_HEIGHT = idle_frame.get_height()

    def create_window(self):
        """Create a resizable window using the current settings dimensions."""
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        try:
            screen = pygame.display.set_mode(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                pygame.SCALED | pygame.DOUBLEBUF,
                vsync=1
            )
        except TypeError:
            # Older pygame versions may not support vsync kwarg; fall back quietly.
            screen = pygame.display.set_mode(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                pygame.SCALED | pygame.DOUBLEBUF
            )
        self._convert_surfaces_for_display(screen)
        windowed_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        return screen, windowed_size

    def draw_hud(self, surface, font, score, high_score, kill_counter, x=10, y=10):
    
        self.score = score 
        self.high_score = high_score 
        self.kill_counter = kill_counter

        if self.score > self.high_score:
            self.high_score = self.score

        panel_rect = self.WOOD_PANEL_IMAGE.get_rect(topleft=(x, y))
        surface.blit(self.WOOD_PANEL_IMAGE, panel_rect)

        score_surf = font.render(f"Score: {self.score}", True, (245, 245, 220))
        best_surf  = font.render(f"Best: {self.high_score}", True, (245, 245, 220))
        kill_surf  = font.render(f"Kills: {self.kill_counter}", True, (245, 245, 220))

        left_x = panel_rect.left
    
        section_height = panel_rect.height / 3
    
        score_rect = score_surf.get_rect(midleft=(left_x + 20 , panel_rect.top + (section_height * 0.5 + 10)))
        best_rect = best_surf.get_rect(midleft=(left_x + 20, panel_rect.top + (section_height * 1.5)))
        kill_rect = kill_surf.get_rect(midleft=(left_x + 20, panel_rect.top + (section_height * 2.5 - 10)))


        surface.blit(score_surf, score_rect)
        surface.blit(best_surf, best_rect)
        surface.blit(kill_surf, kill_rect)



    def draw_lives(self, surface, player):
        """Draw the player's remaining lives as hearts on the top-right of the screen."""
        if not hasattr(player, "lives"):
            return
        heart_image = self.BLUE_HEART_SCALED if getattr(player, "has_shield", False) else self.RED_HEART_SCALED
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

    def _convert_surfaces_for_display(self, screen):
        """Convert all loaded surfaces after a display mode is set (required for convert_alpha)."""
        if self._surfaces_converted:
            return
        if pygame.display.get_surface() is None:
            return
        try:
            self.SPEAR_IMAGE = self.SPEAR_IMAGE.convert_alpha()
            self.BADDIE_IMAGE = self.BADDIE_IMAGE.convert_alpha()
            self.PLATFORM_IMAGE = self.PLATFORM_IMAGE.convert_alpha()
            self.GROUND_IMAGE = self.GROUND_IMAGE.convert_alpha()
            self.MAIN_MENU_IMAGE = self.MAIN_MENU_IMAGE.convert()
            self.PAUSED_MENU_IMAGE = self.PAUSED_MENU_IMAGE.convert()
            self.HELP_MENU_IMAGE = self.HELP_MENU_IMAGE.convert()
            self.HELP_ICON = self.HELP_ICON.convert_alpha()
            self.GRASS_IMAGE = self.GRASS_IMAGE.convert_alpha()
            self.BACKGROUND_LAYERS = [img.convert_alpha() for img in self.BACKGROUND_LAYERS]
            self.RED_HEART_IMAGE = self.RED_HEART_IMAGE.convert_alpha()
            self.BLUE_HEART_IMAGE = self.BLUE_HEART_IMAGE.convert_alpha()
            self.SHIELD_EFFECT_IMAGE = self.SHIELD_EFFECT_IMAGE.convert_alpha()
            self.SHIELD_PICKUP_IMAGE = self.SHIELD_PICKUP_IMAGE.convert_alpha()
            self.DRAGON_IMAGE = self.DRAGON_IMAGE.convert_alpha()
            self.FIREBALL_IMAGE = self.FIREBALL_IMAGE.convert_alpha()
        except pygame.error:
            # If conversion fails, skip to avoid crashing (e.g., when no surface exists).
            return
        self._surfaces_converted = True
        # Rebuild scaled frames from the converted originals.
        self._build_scaled_player_images(self.PLAYER_HEIGHT)
        self._scale_ui_surfaces()

    def _scale_ui_surfaces(self):
        """Scale UI assets (hearts) to current dimensions."""
        try:
            self.RED_HEART_SCALED = pygame.transform.scale(
                self.RED_HEART_IMAGE, (self.PLAYER_LIVES_DISPLAY_SIZE, self.PLAYER_LIVES_DISPLAY_SIZE)
            )
            self.BLUE_HEART_SCALED = pygame.transform.scale(
                self.BLUE_HEART_IMAGE, (self.PLAYER_LIVES_DISPLAY_SIZE, self.PLAYER_LIVES_DISPLAY_SIZE)
            )
        except pygame.error:
            self.RED_HEART_SCALED = self.RED_HEART_IMAGE
            self.BLUE_HEART_SCALED = self.BLUE_HEART_IMAGE


settings = Settings()
