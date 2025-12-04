import pygame 

# settingspy
class Settings:
    # Window
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60
        
    # Colors
    TEXT_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (255, 255, 255)

    # Background
    BACKGROUND_SCROLL_SPEED = 5

    # Ground
    GROUND_HEIGHT = 10
        
    # Player
    PLAYER_SIZE = 40
    PLAYER_JUMP_STRENGTH = 30 # How high the player can jump
    HORIZONTAL_ACCELERATION = 2 # How quickly the player speeds up
    HORIZONTAL_FRICTION = 0.3 # Friction
    VERTICAL_ACCELERATION = 1 # Gravity
        
    # Baddie
    BADDIE_MIN_SIZE = 10
    BADDIE_MAX_SIZE = 40
    BADDIE_MIN_SPEED = BACKGROUND_SCROLL_SPEED + 1
    BADDIE_MAX_SPEED = BACKGROUND_SCROLL_SPEED + 8
    ADD_NEW_BADDIE_RATE = 8

    # Platform
    PLATFORM_HEIGHT = 30
    PLATFORM_WIDTH = 150
    PLATFORM_SPEED = BACKGROUND_SCROLL_SPEED + 5
    ADD_NEW_PLATFORM_RATE = 20

    # Images 
    PLAYER_IMAGE = pygame.image.load('player.png')
    BADDIE_IMAGE = pygame.image.load('baddie.png')
    PLATFORM_IMAGE = pygame.image.load('platform.png')
    BACKGROUND_IMAGE = pygame.image.load('background.png')
    GROUND_IMAGE = pygame.image.load('platform.png')