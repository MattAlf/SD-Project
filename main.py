# main.py
import pygame, random, sys
from pygame.locals import *

# On importe nos modules persos
from settings import Config
from sprites import Player, Baddie, Platform

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

if __name__ == '__main__':
    game = Game()
    game.run()