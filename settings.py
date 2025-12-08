import os
import pygame
from pathlib import Path  # Used to locate asset files relative to this script.


class Settings:
    """Stores tunable values and scales them to the current screen size."""

    BASE_WIDTH = 800  # Reference width for scaling.
    BASE_HEIGHT = 600  # Reference height for scaling.
    DEFAULT_WINDOW_WIDTH = 800  # Default windowed width.
    DEFAULT_WINDOW_HEIGHT = 600  # Default windowed height.

    def __init__(self):
        if not pygame.get_init():
            pygame.init()  # Ensure pygame is ready before loading assets.

        self.FPS = 60  # Target frames per second.
        self.TEXT_COLOR = (0, 0, 0)  # Default UI text color.
        self.BACKGROUND_COLOR = (255, 255, 255)  # Default background fill.
        self.BACKGROUND_SCROLL_SPEED_MULTIPLICATOR = 0.7  # Parallax base speed.

        assets_dir = Path(__file__).parent  # Folder containing assets.
        # Load raw; we'll convert after a display mode is set.
        self.PLAYER_IMAGE = pygame.image.load(assets_dir / "player.png")
        self.SPEAR_IMAGE = pygame.image.load(assets_dir / "spear.png")
        self.BADDIE_IMAGE = pygame.image.load(assets_dir / "baddie.png")
        self.PLATFORM_IMAGE = pygame.image.load(assets_dir / "platform.png")
        self.GROUND_IMAGE = pygame.image.load(assets_dir / "platform.png")
        self.MAIN_MENU_IMAGE = pygame.image.load(assets_dir / "Main.png")
        self.PAUSED_IMAGE = pygame.image.load(assets_dir / "Pause.png")
        self.GRASS_IMAGE = pygame.image.load(assets_dir / "background_layers/grass.png")
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
        self.GAME_OVER_SOUND = pygame.mixer.Sound(assets_dir / "gameover.wav")
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
        self._base_platform_rate = 60  # Base spawn cadence for platforms.

        # Initialize with the base size; the game will call resize with the actual display size.
        self.resize(self.BASE_WIDTH, self.BASE_HEIGHT)

    def resize(self, width: int, height: int):
        self.WINDOW_WIDTH = int(width)  # Actual window width in pixels.
        self.WINDOW_HEIGHT = int(height)  # Actual window height in pixels.

        scale_x = self.WINDOW_WIDTH / self.BASE_WIDTH  # Horizontal scale ratio.
        scale_y = self.WINDOW_HEIGHT / self.BASE_HEIGHT  # Vertical scale ratio.
        self.SCALE = min(scale_x, scale_y)  # Use the limiting scale to preserve aspect.
        s = self.SCALE  # Convenience alias.

        # World sizing (scaled by s with minimums to keep things visible).
        self.GROUND_HEIGHT = max(8, int(10 * s))
        self.PLATFORM_HEIGHT = max(30, int(30 * s))
        self.PLATFORM_WIDTH = max(120, int(250 * s))
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

        self.BADDIE_MIN_SIZE = max(20, int(30 * s))
        self.BADDIE_MAX_SIZE = max(self.BADDIE_MIN_SIZE, int(40 * s))
        self.BADDIE_MIN_SPEED = max(2, int(2 * s))
        self.BADDIE_MAX_SPEED = max(self.BADDIE_MIN_SPEED + 1, int(8 * s))

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

    def build_static_layers(self):
        """Create background and ground sprite groups sized to the current window."""
        from entity import Background, Ground  # Local import to avoid circular dependency on load.

        bg_group = pygame.sprite.Group()
        for image, scrolling_speed in self.BACKGROUND_IMAGES_AND_SPEEDS:
            bg_group.add(Background(image, scrolling_speed, 0, 0))
            bg_group.add(Background(image, scrolling_speed, self.WINDOW_WIDTH, 0))
            bg_group.add(Background(image, scrolling_speed, 2 * self.WINDOW_WIDTH, 0))

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
        screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        self._convert_surfaces_for_display(screen)
        windowed_size = (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        return screen, windowed_size

    def draw_score(self, surface, font, score, x=10, y=0, color=(0, 0, 122)):
        """Render the score text to the given surface."""
        text_surface = font.render(f"Score: {score}", True, color)
        text_rect = text_surface.get_rect(topleft=(x, y))
        surface.blit(text_surface, text_rect)

    def initialize_static_layers(self, screen):
        """Build and draw static layers once at startup."""
        self.background_group, self.ground_group = self.build_static_layers()
        self.background_group.draw(screen)
        self.ground_group.draw(screen)

    def rebuild_static_layers(self, screen):
        """Rebuild static layers to match current window size."""
        self.background_group, self.ground_group = self.build_static_layers()
        return self.background_group, self.ground_group

    def _convert_surfaces_for_display(self, screen):
        """Convert all loaded surfaces after a display mode is set (required for convert_alpha)."""
        if self._surfaces_converted:
            return
        if pygame.display.get_surface() is None:
            return
        try:
            self.PLAYER_IMAGE = self.PLAYER_IMAGE.convert_alpha()
            self.SPEAR_IMAGE = self.SPEAR_IMAGE.convert_alpha()
            self.BADDIE_IMAGE = self.BADDIE_IMAGE.convert_alpha()
            self.PLATFORM_IMAGE = self.PLATFORM_IMAGE.convert_alpha()
            self.GROUND_IMAGE = self.GROUND_IMAGE.convert_alpha()
            self.MAIN_MENU_IMAGE = self.MAIN_MENU_IMAGE.convert()
            self.PAUSED_IMAGE = self.PAUSED_IMAGE.convert()
            self.GRASS_IMAGE = self.GRASS_IMAGE.convert_alpha()
            self.BACKGROUND_LAYERS = [img.convert_alpha() for img in self.BACKGROUND_LAYERS]
        except pygame.error:
            # If conversion fails, skip to avoid crashing (e.g., when no surface exists).
            return
        self._surfaces_converted = True
        # Rebuild scaled frames from the converted originals.
        self._build_scaled_player_images(self.PLAYER_HEIGHT)


settings = Settings()
