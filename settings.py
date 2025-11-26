# settings.py

class Config:
    # Fenêtre
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    CAPTION = 'Dodger Refactored'
    FPS = 60

    # Couleurs
    TEXT_COLOR = (0, 0, 0)
    BG_COLOR = (255, 255, 255)

    # Entités
    BADDIE_MIN_SIZE = 10
    BADDIE_MAX_SIZE = 40
    BADDIE_MIN_SPEED = 1
    BADDIE_MAX_SPEED = 8
    ADD_BADDIE_RATE = 10
    
    PLATFORM_ADD_RATE = 10
    PLATFORM_WIDTH = 50
    PLATFORM_HEIGHT = 10
    PLATFORM_SPEED = 1
    
    PLAYER_SPEED = 5
    GRAVITY = 0.8
    JUMP_STRENGTH = -15
    