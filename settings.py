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

    PLAYER_HEIGHT = 200 # The number to change to manipulate the player's size.
    PLAYER_HITBOX_IMAGE_WIDTH_FACTOR = 0.17 # ~ 300 pixels wide (original image, the width of the knight without the spear) / 1800 pixels wide (original image, the whole image)
    PLAYER_HITBOX_IMAGE_HEIGHT_FACTOR = 0.50 # ~ 500 pixels high (original image, the height of the knight) / 1000 pixels high (original image, the whole image)
    PLAYER_HITBOX_X_OFFSET_FACTOR = 0.42 # ~ 800 pixels horizontal distance (original image, from the left side of the image to the knight) / 1800 pixels wide (original image, the whole image)
    PLAYER_HITBOX_Y_OFFSET_FACTOR = 0.33 # ~ 300 pixels vertical distance (original image, from the bottom of the image to the knight) / 1000 pixels high (original image, the whole image)
    PLAYER_JUMP_STRENGTH = 20 # How high the player can jump.
    PLAYER_ANIMATION_SLOWER = 2 # The higher the number, the slower the player animation speed.

    # Spear
    SPEAR_WIDTH = 100
    SPEAR_SPEED = 20
    SPEAR_ATTACK_COOLDOWN = 500

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
   
