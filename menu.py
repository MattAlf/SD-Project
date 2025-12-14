# menu.py - UI components for main/options/pause menus.
import pygame
from pygame.locals import *
from settings import settings, terminate

BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, PANEL_SPACING = 260, 45, 20, 10
BUTTON_BASE = (20, 20, 20, 180)
BUTTON_BORDER = (255, 255, 255, 180)
BUTTON_TEXT_COLOR = (255, 255, 255, 255)
HELP_BUTTON_SIZE = 70
HELP_BUTTON_MARGIN = 12
FULLSCREEN_BUTTON_SIZE = 70
FULLSCREEN_BUTTON_MARGIN = 12

def build_help_button(font):
    rect = pygame.Rect(
        settings.WINDOW_WIDTH - HELP_BUTTON_SIZE - HELP_BUTTON_MARGIN,
        HELP_BUTTON_MARGIN,
        HELP_BUTTON_SIZE,
        HELP_BUTTON_SIZE
    )
    return Button(
        text = '',
        rect = rect,
        font = font,
        icon = settings.HELP_ICON
    )

def build_fullscreen_button(font):
    rect = pygame.Rect(
        FULLSCREEN_BUTTON_MARGIN,
        FULLSCREEN_BUTTON_MARGIN,
        FULLSCREEN_BUTTON_SIZE,
        FULLSCREEN_BUTTON_SIZE
    )
    return Button(
        text = '',
        rect = rect,
        font = font,
        icon = settings.FULLSCREEN_ICON
    )

def build_buttons(labels, font, center_ratio=0.5):
    total_height = len(labels) * BUTTON_HEIGHT + (len(labels) - 1) * BUTTON_SPACING
    x_left = settings.WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2
    y_start = int((settings.WINDOW_HEIGHT * center_ratio) - (total_height // 2))
    button_list = []
    for i, text in enumerate(labels):
        button_list.append(
            Button(
                text = text,
                rect = (x_left, y_start + (i * (BUTTON_HEIGHT + BUTTON_SPACING)), BUTTON_WIDTH, BUTTON_HEIGHT),
                font = font
                )
            )
    return button_list

class Button:
    def __init__(self, text, rect, font, icon=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.icon = icon

    def draw(self, surface):
        button_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(button_surface, BUTTON_BASE, button_surface.get_rect(), border_radius=8)
        pygame.draw.rect(button_surface, BUTTON_BORDER, button_surface.get_rect(), width=2, border_radius=8)
        if self.icon:
            icon_rect = self.icon.get_rect(center=button_surface.get_rect().center)
            button_surface.blit(self.icon, icon_rect)
        else:
            text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=button_surface.get_rect().center)
            button_surface.blit(text_surf, text_rect)

        surface.blit(button_surface, self.rect.topleft)

    def is_clicked(self, event):
        if event.type == MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            settings.ALL_SOUND_EFFECTS['BUTTON_CLICK'].play()
            return True

# Drag-able horizontal volume slider.
class VolumeSlider:
    def __init__(self, centerx, centery, width=260, height=16, knob_radius=12):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (centerx, centery)
        self.knob_radius = knob_radius
        self.dragging = False
        self.value = 0.5
        self._update_knob_position()

    def _update_knob_position(self):
        knob_centerx = self.rect.left + int(self.value * self.rect.width)
        self.knob_center = (knob_centerx, self.rect.centery)

    def set_value(self, new_volume_value):
        self.value = max(0.0, min(1.0, new_volume_value))
        self._update_knob_position()

    def handle_event(self, event):
        changed = False
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_value_from_pos(event.pos[0])
                changed = True
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self.set_value_from_pos(event.pos[0])
            changed = True
        return changed

    def set_value_from_pos(self, x_pos):
        new_volume_value = (x_pos - self.rect.left) / self.rect.width
        self.set_value(new_volume_value)

    def draw(self, surface):
        track_color = (40, 40, 40, 180)
        fill_color = (200, 200, 200, 220)
        knob_color = (255, 255, 255, 255)
        border_color = (255, 255, 255, 180)
        filling_height = 6
        filling_x_offset = 4

        slider_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(slider_surface, track_color, slider_surface.get_rect(), border_radius=8)
        pygame.draw.rect(
            slider_surface,
            fill_color,
            pygame.Rect(
                filling_x_offset,
                (self.rect.height // 2) - (filling_height // 2),
                int(self.value * self.rect.width),
                filling_height
            ),
            border_radius=4
        )
        pygame.draw.rect(slider_surface, border_color, slider_surface.get_rect(), width=2, border_radius=8)
        pygame.draw.circle(
            slider_surface,
            knob_color,
            ((self.knob_center[0] - self.rect.left), (self.knob_center[1] - self.rect.top)),
            self.knob_radius,
        )
        surface.blit(slider_surface, self.rect.topleft)

class StoryMenu:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        self.buttons = build_buttons(['Back'], self.font, center_ratio=0.92)
        self.fullscreen_button = build_fullscreen_button(self.font)

    def draw(self, surface):
        surface.blit(settings.STORY_MENU_IMAGE, (0, 0))  # Paint background.
        for button in self.buttons:  # Draw menu buttons.
            button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return 'BACK'
        for i, button in enumerate(self.buttons):
            if button.is_clicked(event):
                if i == 0:
                    return 'BACK'
        return None

class HelpMenu:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        self.buttons = build_buttons(['Back'], self.font, center_ratio=0.85)
        self.fullscreen_button = build_fullscreen_button(self.font)

    def draw(self, surface):
        surface.blit(settings.HELP_MENU_IMAGE, (0, 0))  # Paint background.
        for button in self.buttons:  # Draw menu buttons.
            button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return 'BACK'
        for i, button in enumerate(self.buttons):
            if button.is_clicked(event):
                if i == 0:
                    return 'BACK'
        return None
class MainMenu:
    def __init__(self, font):
        self.font = font

        self.create_buttons()

    def create_buttons(self):
        self.buttons = build_buttons(['Start Game', 'Options', 'Story', 'Exit'], self.font, center_ratio=0.6)
        self.help_button = build_help_button(self.font)
        self.fullscreen_button = build_fullscreen_button(self.font)

    def draw(self, surface):
        surface.blit(settings.MAIN_MENU_IMAGE, (0, 0))  # Paint background.
        for button in self.buttons:  # Draw menu buttons.
            button.draw(surface)
        self.help_button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        if self.help_button.is_clicked(event):
            return 'HELP'
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'
        for i, button in enumerate(self.buttons):
            if button.is_clicked(event):
                if i == 0:
                    return 'START_GAME'
                elif i == 1:
                    return 'OPTIONS'
                elif i == 2:
                    return 'STORY'
                elif i == 3:
                    return 'EXIT'
        return None

class OptionsMenu:
    def __init__(self, font):
        self.font = font
        self.music_volume = settings.music_volume
        self.sound_effects_volume = settings.sound_effects_volume

        self.create_buttons()

    def draw(self, surface):
        surface.blit(settings.OPTIONS_MENU_IMAGE, (0, 0))

        # Draw fullscreen + back buttons
        for button in self.buttons:
            button.draw(surface)

        self.sound_effects_slider.draw(surface)
        self.sound_effects_panel[0].draw(surface)
        self.music_slider.draw(surface)
        self.music_panel[0].draw(surface)

        self.help_button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        # --- Handle music slider ---
        if self.music_slider.handle_event(event):
            self.music_volume = self.music_slider.value
            pygame.mixer.music.set_volume(self.music_volume)
            settings.music_volume = self.music_volume
            self.music_panel[0].text = f'Music: {int(self.music_volume * 100)}%'
            return None

        # --- Handle SFX slider ---
        if self.sound_effects_slider.handle_event(event):
            self.sound_effects_volume = self.sound_effects_slider.value
            settings.sound_effects_volume = self.sound_effects_volume
            self.sound_effects_panel[0].text = f'Sounds: {int(self.sound_effects_volume * 100)}%'
            # Apply new volume to all SFX
            for sound in settings.ALL_SOUND_EFFECTS.values():
                sound.set_volume(self.sound_effects_volume)
            return None

        # Escape → back
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return 'BACK'

        # Help button
        if self.help_button.is_clicked(event):
            return 'HELP'
        
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'
        
        # Regular buttons
        for i, button in enumerate(self.buttons):
            if button.is_clicked(event):
                if i == 0:
                    return 'BACK'
        return None

    def create_buttons(self):
        self.buttons = build_buttons(['Back'], self.font)
        # Push buttons down to give slider more breathing room.
        self.buttons_total_height = (len(self.buttons) * BUTTON_HEIGHT) + ((len(self.buttons) - 1) * BUTTON_SPACING)
        for button in self.buttons:
            button.rect.y += self.buttons_total_height // 2 + BUTTON_SPACING
        
        self.help_button = build_help_button(self.font)
        self.fullscreen_button = build_fullscreen_button(self.font)

        # SFX slider under it
        self.sound_effects_slider = VolumeSlider(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2)
        self.sound_effects_slider.set_value(self.sound_effects_volume)# Sync slider knob to current volume.

        self.sound_effects_panel = build_buttons([f'Sounds: {int(self.sound_effects_volume * 100)}%'], self.font)
        self.sound_effects_panel[0].rect.bottom = self.sound_effects_slider.rect.top - PANEL_SPACING
        
        # Music slider at upper-middle
        self.music_slider = VolumeSlider(settings.WINDOW_WIDTH // 2, (settings.WINDOW_HEIGHT // 2) - 90)
        self.music_slider.set_value(self.music_volume)# Sync slider knob to current volume.

        self.music_panel = build_buttons([f'Music: {int(self.music_volume * 100)}%'], self.font)
        self.music_panel[0].rect.bottom = self.music_slider.rect.top - PANEL_SPACING

class PauseMenu:
    def __init__(self, font):
        self.font = font

        self.create_buttons()

    def create_buttons(self):
        self.buttons = build_buttons(['Resume', 'Main Menu', 'Exit Game'], self.font, center_ratio=0.6)
        self.help_button = build_help_button(self.font)
        self.fullscreen_button = build_fullscreen_button(self.font)

    def draw(self, surface):
        surface.blit(settings.PAUSED_MENU_IMAGE, (0, 0))

        for b in self.buttons:
            b.draw(surface)

        self.help_button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return 'RESUME'
        
        if self.help_button.is_clicked(event):
            return 'HELP'
        
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'

        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                if i == 0:
                    return 'RESUME'
                elif i == 1:
                    return 'MAIN_MENU'
                elif i == 2:
                    return 'EXIT'
        return None

class GameOverMenu:
    def __init__(self, font):
        self.font = font

        self.create_buttons()

    def create_buttons(self):
        self.buttons = build_buttons(['Retry', 'Main Menu', 'Exit'], self.font, center_ratio=0.6)
        self.help_button = build_help_button(self.font)
        self.fullscreen_button = build_fullscreen_button(self.font)

    def draw(self, surface, score, kill_counter):
        surface.blit(settings.GAME_OVER_MENU_IMAGE, (0, 0))

        score_text = self.font.render(f'Score: {score}', True, 'white')
        score_rect = score_text.get_rect(center=(settings.WINDOW_WIDTH // 2, self.buttons[0].rect.top - 20))
        surface.blit(score_text, score_rect)

        kill_counter_text = self.font.render(f'Kills: {kill_counter}', True, 'white')
        kill_counter_rect = kill_counter_text.get_rect(center=(settings.WINDOW_WIDTH // 2, (score_rect.top - 20)))
        surface.blit(kill_counter_text, kill_counter_rect)

        highest_score_text = self.font.render(f'Highest score: {settings.highest_score}', True, 'white')
        highest_score_rect = highest_score_text.get_rect(center=(settings.WINDOW_WIDTH // 2, (kill_counter_rect.top - 20)))
        surface.blit(highest_score_text, highest_score_rect)

        for b in self.buttons:
            b.draw(surface)

        self.help_button.draw(surface)
        self.fullscreen_button.draw(surface)

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return 'MAIN_MENU'
        
        if self.help_button.is_clicked(event):
            return 'HELP'
        
        if self.fullscreen_button.is_clicked(event):
            return 'TOGGLE_FULLSCREEN'

        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                if i == 0:
                    return 'RETRY'
                if i == 1:
                    return 'MAIN_MENU'
                if i == 2:
                    return 'EXIT'
        return None

def run_main_menu(screen, main_menu, options_menu, help_menu, story_menu, clock):
    '''Main menu loop; exits when the user starts the game or quits.'''
    pygame.mixer.music.load(settings.assets_dir / 'musics/menu_music.wav')
    pygame.mixer.music.play(-1, 0.0)
    current_menu = 'MAIN'  # Tracks whether we are in the main or options menu.
    while True:
        for event in pygame.event.get():  # Poll menu events.
            if event.type == QUIT:
                terminate()

            if current_menu == 'MAIN':
                result = main_menu.handle_event(event)
                if result == 'START_GAME':
                    return
                elif result == 'OPTIONS':
                    current_menu = 'OPTIONS'
                elif result == 'HELP':
                    current_menu = 'HELP'
                elif result == 'TOGGLE_FULLSCREEN':
                    toggle_fullscreen(screen)
                elif result == 'STORY':
                    current_menu = 'STORY'
                elif result == 'EXIT':
                    terminate()

            elif current_menu == 'OPTIONS':
                result = options_menu.handle_event(event)
                if result == 'HELP':
                    current_menu = 'HELP'
                elif result == 'TOGGLE_FULLSCREEN':
                    toggle_fullscreen(screen)
                elif result == 'BACK':
                    current_menu = 'MAIN'
            
            elif current_menu == 'HELP':
                result = help_menu.handle_event(event)
                if result == 'BACK':
                    current_menu = 'MAIN'
                elif result == 'TOGGLE_FULLSCREEN':
                    toggle_fullscreen(screen)

            elif current_menu == 'STORY':
                result = story_menu.handle_event(event)
                if result == 'BACK':
                    current_menu = 'MAIN'
                elif result == 'TOGGLE_FULLSCREEN':
                    toggle_fullscreen(screen)
                    
        if current_menu == 'MAIN':
            main_menu.draw(screen)
        elif current_menu == 'HELP':
            help_menu.draw(screen)
        elif current_menu == 'OPTIONS':
            options_menu.draw(screen)
        elif current_menu == 'STORY':
            story_menu.draw(screen)

        pygame.display.update()
        clock.tick(settings.FPS)

def toggle_fullscreen(screen):
    '''Toggle fullscreen/windowed modes and refresh layout-dependent assets.'''

    if settings.is_fullscreen:
        # Switch to windowed
        try:
            screen = pygame.display.set_mode(
                settings.WINDOW_DIMENSIONS,
                pygame.SCALED | pygame.DOUBLEBUF,
                vsync=1
            )
        except pygame.error:
            # Fallback: minimal window
            screen = pygame.display.set_mode(
                settings.WINDOW_DIMENSIONS,
                pygame.SCALED | pygame.DOUBLEBUF
            )
        settings.is_fullscreen = False
    else:
        # Switch to fullscreen
        try:
            screen = pygame.display.set_mode(
                settings.WINDOW_DIMENSIONS,
                pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF,
                vsync=1
            )
        except pygame.error:
            # Fallback: plain fullscreen
            screen = pygame.display.set_mode(
                settings.WINDOW_DIMENSIONS,
                pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF
            )
        settings.is_fullscreen = True
