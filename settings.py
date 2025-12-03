# settings.py
class Settings:
    def __init__(self):
        # Window
        self.WINDOW_WIDTH = 600
        self.WINDOW_HEIGHT = 600
        self.FPS = 60
        
        # Colors
        self.TEXT_COLOR = (0, 0, 0)
        self.BACKGROUND_COLOR = (255, 255, 255)

        # Background
        self.BACKGROUND_SCROLL_SPEED = 1
        
        # Player
        self.PLAYER_MOVE_RATE = 5
        self.PLAYER_SIZE = 40
        self.PLAYER_GRAVITY = 0.5
        self.PLAYER_JUMP_STRENGTH = -10
        
        # Baddie
        self.BADDIE_MIN_SIZE = 10
        self.BADDIE_MAX_SIZE = 40
        self.BADDIE_MIN_SPEED = 1
        self.BADDIE_MAX_SPEED = 8
        self.ADD_NEW_BADDIE_RATE = 6

        # Platform
        self.PLATFORM_HEIGHT = 20
