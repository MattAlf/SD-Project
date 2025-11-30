# sprites.py
import pygame, random, sys
from settings import Config 

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Player(Entity):
    def __init__(self, x, y):
        img = pygame.image.load('player.png') if 'player.png' in sys.modules else pygame.Surface((20, 20))
        if not 'player.png' in sys.modules: img.fill((255, 0, 0)) 
        super().__init__(img, x, y)
        self.vel_y = 0
        self.on_ground = False
        self.move_left = False
        self.move_right = False

    def update(self, platforms):
        # Mouvement Horizontal
        if self.move_left and self.rect.left > 0:
            self.rect.x -= Config.PLAYER_SPEED
        if self.move_right and self.rect.right < Config.WINDOW_WIDTH:
            self.rect.x += Config.PLAYER_SPEED

        # Gravité et Mouvement Vertical
        self.vel_y += Config.GRAVITY
        self.rect.y += self.vel_y

        # Collision Sol (Bas de l'écran)
        if self.rect.bottom >= Config.WINDOW_HEIGHT:
            self.rect.bottom = Config.WINDOW_HEIGHT
            self.vel_y = 0
            self.on_ground = True

        # Collision Plateformes (Uniquement si on tombe)
        self.check_platform_collisions(platforms)

    def check_platform_collisions(self, platforms):
        if self.vel_y > 0: # On ne collisionne que si on descend
            hits = pygame.sprite.spritecollide(self, platforms, False)
            for platform in hits:
                # Vérification fine: on doit être au-dessus de la plateforme
                if self.rect.bottom <= platform.rect.bottom + self.vel_y: 
                    self.rect.bottom = platform.rect.top
                    self.vel_y = Config.PLATFORM_SPEED # On suit la vitesse de la plateforme
                    self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = Config.JUMP_STRENGTH
            self.on_ground = False

class Baddie(Entity):
    def __init__(self):
        size = random.randint(Config.BADDIE_MIN_SIZE, Config.BADDIE_MAX_SIZE)
        img = pygame.image.load('baddie.png') if 'baddie.png' in sys.modules else pygame.Surface((size, size))
        if not 'baddie.png' in sys.modules: img.fill((0, 255, 0))
        img = pygame.transform.scale(img, (size, size))
        
        x = random.randint(0, Config.WINDOW_WIDTH - size)
        y = 0 - size
        super().__init__(img, x, y)
        self.speed = random.randint(Config.BADDIE_MIN_SPEED, Config.BADDIE_MAX_SPEED)

    def update(self, reverse=False, slow=False):
        if reverse:
            self.rect.y -= 5
        elif slow:
            self.rect.y += 1
        else:
            self.rect.y += self.speed
        
        if self.rect.top > Config.WINDOW_HEIGHT:
            self.kill() # Se supprime lui-même du groupe de sprites

class Platform(Entity):
    def __init__(self, x, y):
        img = pygame.image.load('plateforme.png') if 'plateforme.png' in sys.modules else pygame.Surface((Config.PLATFORM_WIDTH, Config.PLATFORM_HEIGHT))
        if not 'plateforme.png' in sys.modules: img.fill((0, 0, 255))
        img = pygame.transform.scale(img, (Config.PLATFORM_WIDTH, Config.PLATFORM_HEIGHT))
        
        super().__init__(img, x, y)

    def update(self):
        self.rect.y += Config.PLATFORM_SPEED
        if self.rect.top > Config.WINDOW_HEIGHT:
            self.kill()