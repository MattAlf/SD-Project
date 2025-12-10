# menu.py - UI components for main/options/pause menus.
import sys
import pygame
from pygame.locals import *
from settings import settings

# --- CONSTANTES DE STYLE ---
class Style:
    BUTTON_W, BUTTON_H = 260, 45
    SPACING = 20
    COLOR_BASE = (20, 20, 20, 180)
    COLOR_BORDER = (255, 255, 255, 180)
    COLOR_HOVER = (60, 60, 60, 180) # Ajout feedback visuel
    COLOR_TEXT = 'white'

# --- WIDGETS UI ---
class UIElement:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.active = True

    def draw(self, surface):
        pass

    def handle_event(self, event):
        return None

    def set_pos(self, x, y):
        self.rect.topleft = (x, y)

class Button(UIElement):
    def __init__(self, text, font, action_id):
        super().__init__((0, 0, Style.BUTTON_W, Style.BUTTON_H))
        self.text = text
        self.font = font
        self.action_id = action_id
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        # Changement de couleur au survol
        color = Style.COLOR_HOVER if self.is_hovered else Style.COLOR_BASE
        
        btn_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, color, btn_surf.get_rect(), border_radius=8)
        pygame.draw.rect(btn_surf, Style.COLOR_BORDER, btn_surf.get_rect(), width=2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, Style.COLOR_TEXT)
        text_rect = text_surf.get_rect(center=btn_surf.get_rect().center)
        btn_surf.blit(text_surf, text_rect)
        
        surface.blit(btn_surf, self.rect.topleft)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        # Logique modifiée : On détecte l'appui (DOWN) pour l'effet visuel,
        # mais on valide l'action au relâchement (UP). 
        # Cela évite les conflits lors du changement d'écran.
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return self.action_id
            self.is_pressed = False
            
        return None

class VolumeSlider(UIElement):
    def __init__(self, font, width=260):
        super().__init__((0, 0, width, 50))
        self.font = font
        self.value = pygame.mixer.music.get_volume()
        self.dragging = False
        self.track_rect = pygame.Rect(0, 0, width, 16) 

    def draw(self, surface):
        label = self.font.render(f'Volume: {int(self.value * 100)}%', True, Style.COLOR_TEXT)
        label_rect = label.get_rect(centerx=self.rect.centerx, top=self.rect.top)
        surface.blit(label, label_rect)

        self.track_rect.center = (self.rect.centerx, self.rect.bottom - 10)
        
        pygame.draw.rect(surface, (40, 40, 40), self.track_rect, border_radius=8)
        
        fill_width = int(self.value * self.track_rect.width)
        fill_rect = pygame.Rect(self.track_rect.left, self.track_rect.top, fill_width, self.track_rect.height)
        pygame.draw.rect(surface, (200, 200, 200), fill_rect, border_radius=8)
        
        knob_x = self.track_rect.left + fill_width
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, self.track_rect.centery), 10)
        pygame.draw.circle(surface, (20, 20, 20), (knob_x, self.track_rect.centery), 10, width=1)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.track_rect.inflate(10, 10).collidepoint(event.pos):
                self.dragging = True
                self._update_val(event.pos[0])
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self._update_val(event.pos[0])
        return None

    def _update_val(self, mouse_x):
        rel = (mouse_x - self.track_rect.left) / self.track_rect.width
        self.value = max(0.0, min(1.0, rel))
        pygame.mixer.music.set_volume(self.value)

# --- SYSTÈME DE MENUS ---

class BaseMenu:
    def __init__(self, font, bg_image):
        self.font = font
        self.bg_image_original = bg_image
        self.elements = []
        self.scaled_bg = None
        self.refresh_layout()

    def refresh_layout(self):
        screen = pygame.display.get_surface()
        sw, sh = screen.get_size()
        
        if self.bg_image_original:
            self.scaled_bg = pygame.transform.scale(self.bg_image_original, (sw, sh))

        total_h = sum(e.rect.height for e in self.elements) + (len(self.elements) - 1) * Style.SPACING
        start_y = (sh - total_h) // 2
        
        current_y = start_y
        for el in self.elements:
            x = (sw - el.rect.width) // 2
            el.set_pos(x, current_y)
            current_y += el.rect.height + Style.SPACING

    def draw(self, surface):
        if self.scaled_bg:
            surface.blit(self.scaled_bg, (0, 0))
        for el in self.elements:
            el.draw(surface)

    def handle_event(self, event):
        for el in self.elements:
            action = el.handle_event(event)
            if action: 
                return action
        return None

class MainMenu(BaseMenu):
    def __init__(self, font):
        super().__init__(font, settings.MAIN_MENU_IMAGE)
        self.elements = [
            Button("Start Game", font, "START"),
            Button("Options", font, "GOTO_OPTIONS"),
            Button("Exit", font, "EXIT")
        ]
        self.refresh_layout()

class PauseMenu(BaseMenu):
    def __init__(self, font):
        super().__init__(font, settings.PAUSED_IMAGE)
        self.elements = [
            Button("Resume", font, "RESUME"),
            Button("Main Menu", font, "GOTO_MAIN"),
            Button("Exit Game", font, "EXIT")
        ]
        self.refresh_layout()

class OptionsMenu(BaseMenu):
    def __init__(self, font):
        super().__init__(font, settings.MAIN_MENU_IMAGE)
        self.build_elements()
        self.refresh_layout()

    def build_elements(self):
        self.elements = [
            Button("Fullscreen", self.font, "TOGGLE_FULLSCREEN"),
            VolumeSlider(self.font),
            Button("Back", self.font, "BACK")
        ]
    
    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "BACK"
        return super().handle_event(event)

# --- LOGIQUE GLOBALE ---

def toggle_display_mode(screen, windowed_size, all_menus):
    """
    Gère le changement technique de fenêtre.
    Version 'Hard Reset' : Force la recréation du contexte pour éviter le crash macOS.
    """
    is_fullscreen = bool(screen.get_flags() & pygame.FULLSCREEN)
    
    # Nettoyage
    pygame.time.wait(100) 
    pygame.event.clear()

    try:
        if is_fullscreen:
            # --- RETOUR FENÊTRÉ ---
            w, h = int(windowed_size[0]), int(windowed_size[1])
            
            # Astuce : On passe par une étape intermédiaire pour nettoyer le renderer
            tmp = pygame.display.set_mode((1, 1), pygame.NOFRAME)
            pygame.time.wait(50)
            
            # Création propre de la fenêtre
            new_screen = pygame.display.set_mode((w, h), pygame.RESIZABLE, vsync=0)
        else:
            # --- PASSAGE FULLSCREEN ---
            w_curr, h_curr = screen.get_size()
            windowed_size = (int(w_curr), int(h_curr))
            
            target_w = settings.DEFAULT_WINDOW_WIDTH
            target_h = settings.DEFAULT_WINDOW_HEIGHT
            
            # 1. HARD RESET : On tue techniquement la fenêtre actuelle.
            # Cela force macOS à détruire le contexte OpenGL "Windowed" qui entre en conflit.
            tmp = pygame.display.set_mode((1, 1), pygame.NOFRAME)
            pygame.time.wait(100) # Petite pause pour laisser l'OS digérer la destruction
            
            # 2. RENAISSANCE : On crée le contexte Fullscreen Scaled à neuf.
            # vsync=0 est crucial ici aussi.
            new_screen = pygame.display.set_mode(
                (target_w, target_h), 
                pygame.FULLSCREEN | pygame.SCALED, 
                vsync=0
            )

    except pygame.error as e:
        print(f"Erreur fatale affichage : {e}")
        # Fallback de sécurité
        new_screen = pygame.display.set_mode(
            (settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT), 
            pygame.RESIZABLE
        )

    pygame.event.clear()
    
    # Mise à jour settings
    actual_w, actual_h = new_screen.get_size()
    settings.resize(actual_w, actual_h)
    
    # IMPORTANT : Comme on a fait un Hard Reset, il faut être sûr que les surfaces soient compatibles
    settings._surfaces_converted = False # On force la reconversion
    settings._convert_surfaces_for_display(new_screen)
    
    for menu in all_menus:
        menu.refresh_layout()
        
    return new_screen, windowed_size

def run_menu_loop(screen, windowed_size, main_menu, options_menu, pause_menu, clock, start_in_pause=False, rebuild_static_layers=None):
    current_menu = pause_menu if start_in_pause else main_menu
    all_menus = [main_menu, options_menu, pause_menu]

    while True:
        # On limite le FPS du menu pour éviter de surchauffer inutilement
        dt = clock.tick(settings.FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            
            action = current_menu.handle_event(event)
            
            if action == "START":           return "START", screen, windowed_size
            elif action == "RESUME":        return "RESUME", screen, windowed_size
            elif action == "EXIT":          pygame.quit(); sys.exit()
            elif action == "GOTO_OPTIONS":  current_menu = options_menu
            elif action == "GOTO_MAIN":     return "MAIN_MENU", screen, windowed_size 
            elif action == "BACK":          current_menu = pause_menu if start_in_pause else main_menu
            
            elif action == "TOGGLE_FULLSCREEN":
                screen, windowed_size = toggle_display_mode(screen, windowed_size, all_menus)
                if rebuild_static_layers: rebuild_static_layers()

        current_menu.draw(screen)
        pygame.display.update()