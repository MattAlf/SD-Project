import pygame
import random
import sys
from pygame.locals import *

# --- CONFIGURATION ---
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

# --- CLASSES D'ENTITÉS (SPRITES) ---

class Entity(pygame.sprite.Sprite):
    """Classe de base pour tout objet affichable"""
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Player(Entity):
    def __init__(self, x, y):
        # Création d'une surface simple (ou chargement d'image)
        img = pygame.image.load('player.png') if 'player.png' in sys.modules else pygame.Surface((20, 20))
        # Fallback si l'image n'existe pas pour tester le code sans assets
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

# --- MOTEUR DE JEU (GAME ENGINE) ---

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption(Config.CAPTION)
        self.font = pygame.font.SysFont(None, 48)
        
        # Chargement Sons (avec gestion d'erreur basique pour l'exemple)
        try:
            self.game_over_sound = pygame.mixer.Sound('gameover.wav')
            pygame.mixer.music.load('background.mid')
        except:
            self.game_over_sound = None
            print("Warning: Audio files not found.")

        self.running = True
        self.state = "MENU" # MENU, PLAYING, GAMEOVER
        
        # Groupes de Sprites
        self.all_sprites = pygame.sprite.Group()
        self.baddies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.player = None

        # Game State Variables
        self.score = 0
        self.top_score = 0
        self.reverse_cheat = False
        self.slow_cheat = False
        self.baddie_timer = 0
        self.platform_timer = 0

    def new_game(self):
        """Réinitialise le jeu pour une nouvelle partie"""
        self.all_sprites.empty()
        self.baddies.empty()
        self.platforms.empty()
        
        self.player = Player(Config.WINDOW_WIDTH / 2, Config.WINDOW_HEIGHT - 50)
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.reverse_cheat = False
        self.slow_cheat = False
        
        # Génération initiale de plateformes
        num_platforms = 25
        spacing = Config.WINDOW_HEIGHT // (num_platforms + 1)
        for i in range(num_platforms):
            x = random.randint(0, Config.WINDOW_WIDTH - 50)
            y = Config.WINDOW_HEIGHT - (i * spacing) - 50
            p = Platform(x, y)
            self.platforms.add(p)
            self.all_sprites.add(p)

        if self.game_over_sound: pygame.mixer.music.play(-1, 0.0)
        self.state = "PLAYING"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.state == "MENU" or self.state == "GAMEOVER":
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    else:
                        self.new_game()
            
            elif self.state == "PLAYING":
                self.handle_playing_input(event)

    def handle_playing_input(self, event):
        if event.type == KEYDOWN:
            if event.key == K_z: self.reverse_cheat = True
            if event.key == K_x: self.slow_cheat = True
            if event.key in (K_LEFT, K_a): self.player.move_left = True
            if event.key in (K_RIGHT, K_d): self.player.move_right = True
            if event.key in (K_UP, K_w): self.player.jump()
            if event.key == K_ESCAPE: self.running = False

        if event.type == KEYUP:
            if event.key == K_z: self.reverse_cheat = False; self.score = 0
            if event.key == K_x: self.slow_cheat = False; self.score = 0
            if event.key in (K_LEFT, K_a): self.player.move_left = False
            if event.key in (K_RIGHT, K_d): self.player.move_right = False
        
        if event.type == MOUSEMOTION:
            self.player.rect.centerx = event.pos[0]
            self.player.rect.centery = event.pos[1]

    def update(self):
        if self.state != "PLAYING": return

        self.score += 1

        # Spawning Logic
        self.baddie_timer += 1
        if self.baddie_timer == Config.ADD_BADDIE_RATE:
            self.baddie_timer = 0
            b = Baddie()
            self.baddies.add(b)
            self.all_sprites.add(b)

        self.platform_timer += 1
        if self.platform_timer == Config.PLATFORM_ADD_RATE:
            self.platform_timer = 0
            p = Platform(random.randint(0, Config.WINDOW_WIDTH - Config.PLATFORM_WIDTH), -Config.PLATFORM_HEIGHT)
            self.platforms.add(p)
            self.all_sprites.add(p)

        # Updates des sprites
        self.player.update(self.platforms)
        self.platforms.update()
        for b in self.baddies:
            b.update(self.reverse_cheat, self.slow_cheat)

        # Collision Joueur vs Ennemis
        if pygame.sprite.spritecollideany(self.player, self.baddies):
            if self.score > self.top_score:
                self.top_score = self.score
            self.game_over()

    def draw(self):
        self.screen.fill(Config.BG_COLOR)

        if self.state == "MENU":
            self.draw_text('Dodger', Config.WINDOW_WIDTH / 3, Config.WINDOW_HEIGHT / 3)
            self.draw_text('Press a key to start.', Config.WINDOW_WIDTH / 3 - 30, Config.WINDOW_HEIGHT / 3 + 50)
        
        elif self.state == "PLAYING":
            self.all_sprites.draw(self.screen)
            self.draw_text(f'Score: {self.score}', 10, 0)
            self.draw_text(f'Top Score: {self.top_score}', 10, 40)
        
        elif self.state == "GAMEOVER":
            self.all_sprites.draw(self.screen) # On affiche le jeu figé en fond
            self.draw_text('GAME OVER', Config.WINDOW_WIDTH / 3, Config.WINDOW_HEIGHT / 3)
            self.draw_text('Press a key to play again.', Config.WINDOW_WIDTH / 3 - 80, Config.WINDOW_HEIGHT / 3 + 50)

        pygame.display.update()

    def draw_text(self, text, x, y):
        textobj = self.font.render(text, 1, Config.TEXT_COLOR)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.screen.blit(textobj, textrect)

    def game_over(self):
        if self.game_over_sound: 
            pygame.mixer.music.stop()
            self.game_over_sound.play()
        self.state = "GAMEOVER"

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)

# --- EXECUTION ---
if __name__ == '__main__':
    game = Game()
    game.run()