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

    # Ground
    GROUND_HEIGHT = 10

    # Background scroll speed multiplicator. It will speed up the background scrolling speed while keeping the
    # parallax effect in the same proportions. (To avoid bugs don't go below 0.6)
    BACKGROUND_SCROLL_SPEED_MULTIPLICATOR = 0.7
        
    # Player (720 width, 512 height, 12.8 ratio)(image is 1800 par 1000)
    #PLAYER_ORIGINAL_WIDTH = 360
    #PLAYER_ORIGINAL_HEIGHT = 512
    #PLAYER_HEIGHT = 40
    #PLAYER_WIDTH = 56

    PLAYER_HEIGHT = 300
    PLAYER_JUMP_STRENGTH = 20 # How high the player can jump
    PLAYER_ANIMATION_SPEED = 2

    HORIZONTAL_ACCELERATION = 2 # How quickly the player speeds up
    HORIZONTAL_FRICTION = 0.2 # Friction
    VERTICAL_ACCELERATION = 1 # Gravity
        
    # Baddie
    BADDIE_MIN_SIZE = 30
    BADDIE_MAX_SIZE = 40
    BADDIE_MIN_SPEED = 1
    BADDIE_MAX_SPEED = 8
    ADD_NEW_BADDIE_RATE = 16

    # Platform
    PLATFORM_HEIGHT = 30
    PLATFORM_WIDTH = 250
    PLATFORM_SPEED =  5
    ADD_NEW_PLATFORM_RATE = 20
   
