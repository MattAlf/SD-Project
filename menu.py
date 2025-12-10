# menu.py - UI components for main/options/pause menus.
import sys
import pygame
from pygame.locals import *
from settings import settings

BUTTON_W, BUTTON_H, BUTTON_SPACING = 260, 45, 20
BTN_BASE = (20, 20, 20, 180)
BTN_BORDER = (255, 255, 255, 180)


def build_buttons(labels, font, center_ratio=0.5):
    """Return Buttons centered in the current window."""
    screen_w, screen_h = pygame.display.get_surface().get_size()
    total_h = len(labels) * BUTTON_H + (len(labels) - 1) * BUTTON_SPACING
    x = screen_w // 2 - BUTTON_W // 2
    y_start = int(screen_h * center_ratio - total_h // 2)
    return [
        Button(
            text,
            (x, y_start + i * (BUTTON_H + BUTTON_SPACING), BUTTON_W, BUTTON_H),
            font,
        )
        for i, text in enumerate(labels)
    ]


class Button:
    def __init__(self, text, rect, font):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font

    def draw(self, surface):
        btn_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, BTN_BASE, btn_surface.get_rect(), border_radius=8)
        pygame.draw.rect(btn_surface, BTN_BORDER, btn_surface.get_rect(), width=2, border_radius=8)
        text_surf = self.font.render(self.text, True, 'white')
        text_rect = text_surf.get_rect(center=btn_surface.get_rect().center)
        btn_surface.blit(text_surf, text_rect)
        surface.blit(btn_surface, self.rect.topleft)

    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


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
        knob_x = self.rect.left + int(self.value * self.rect.width)
        self.knob_center = (knob_x, self.rect.centery)

    def set_value(self, value: float):
        self.value = max(0.0, min(1.0, value))
        self._update_knob_position()

    def handle_event(self, event):
        changed = False
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_value_from_pos(event.pos[0])
                changed = True
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self._set_value_from_pos(event.pos[0])
            changed = True
        return changed

    def _set_value_from_pos(self, x_pos):
        rel = (x_pos - self.rect.left) / self.rect.width
        self.set_value(rel)

    def draw(self, surface):
        track_color = (40, 40, 40, 180)
        fill_color = (200, 200, 200, 220)
        knob_color = (255, 255, 255, 255)
        border_color = (255, 255, 255, 180)

        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, track_color, surf.get_rect(), border_radius=8)
        pygame.draw.rect(
            surf,
            fill_color,
            pygame.Rect(4, self.rect.height // 2 - 3, max(0, int(self.value * (self.rect.width - 8))), 6),
            border_radius=4,
        )
        pygame.draw.rect(surf, border_color, surf.get_rect(), width=2, border_radius=8)
        pygame.draw.circle(
            surf,
            knob_color,
            (self.knob_center[0] - self.rect.left, self.knob_center[1] - self.rect.top),
            self.knob_radius,
        )
        surface.blit(surf, self.rect.topleft)


class MainMenu:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        self.buttons = build_buttons(['Start Game', 'Options', 'Exit'], self.font)

    def draw(self, surface):
        bg = pygame.transform.scale(settings.MAIN_MENU_IMAGE, surface.get_size())  # Fit background to window.
        surface.blit(bg, (0, 0))  # Paint background.
        for b in self.buttons:  # Draw menu buttons.
            b.draw(surface)

    def handle_event(self, event):
        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                return i
        return None


class OptionsMenu:
    def __init__(self, font):
        self.font = font
        self.volume = pygame.mixer.music.get_volume()
        self.fullscreen = False

        self.buttons = []
        self.slider = None
        self.refresh_layout()

    def draw(self, surface):
        bg = pygame.transform.scale(settings.MAIN_MENU_IMAGE, surface.get_size())  # Fit menu art to window.
        surface.blit(bg, (0, 0))

        if self.slider:  # Volume label + slider.
            panel_w, panel_h = 260, 45
            panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            base_color = (20, 20, 20, 180)
            border_color = (255, 255, 255, 180)
            pygame.draw.rect(panel_surface, base_color, panel_surface.get_rect(), border_radius=8)
            pygame.draw.rect(panel_surface, border_color, panel_surface.get_rect(), width=2, border_radius=8)

            vol_text = self.font.render(f'Volume: {int(self.volume * 100)}%', True, 'white')
            vol_rect = vol_text.get_rect(center=panel_surface.get_rect().center)
            panel_surface.blit(vol_text, vol_rect)

            panel_rect = panel_surface.get_rect(center=(self.slider.rect.centerx, self.slider.rect.top - 35))
            surface.blit(panel_surface, panel_rect)
            self.slider.draw(surface)

        for b in self.buttons:  # Draw buttons (fullscreen/back).
            b.draw(surface)

    def handle_event(self, event):
        if self.slider and self.slider.handle_event(event):
            self.volume = self.slider.value
            pygame.mixer.music.set_volume(self.volume)
            return None

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "BACK"

        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                # Fullscreen button
                if i == 0:
                    # Return an action to main so main can safely change display mode
                    return "TOGGLE_FULLSCREEN"

                # Volume -
                # Back
                elif i == 1:
                    return "BACK"

        return None

    def refresh_layout(self):
        self.buttons = build_buttons(['Fullscreen', 'Back'], self.font)
        for b in self.buttons:
            b.rect.y += 40  # Push buttons down to give slider more breathing room.

        screen_w, screen_h = pygame.display.get_surface().get_size()
        slider_y = max(140, screen_h // 2 - 80)  # Keep slider near upper-middle.
        self.slider = VolumeSlider(screen_w // 2, slider_y)
        self.slider.set_value(self.volume)  # Sync slider knob to current volume.

    def toggle_fullscreen(self, screen, windowed_size, main_menu, pause_menu, game_over_menu):
        """Toggle fullscreen/windowed modes and refresh layout-dependent assets."""
        display_kwargs = {}
        try:
            # Keep fullscreen/windowed transitions on the monitor that currently hosts the window.
            display_kwargs["display"] = pygame.display.get_window_display_index()
        except (pygame.error, AttributeError):
            pass  # Older pygame/SDL versions may not support per-display window queries.

        if self.fullscreen:
            try:
                screen = pygame.display.set_mode(
                    windowed_size,
                    pygame.RESIZABLE | pygame.SCALED | pygame.DOUBLEBUF,
                    vsync=1,
                    **display_kwargs
                )
            except TypeError:
                screen = pygame.display.set_mode(
                    windowed_size,
                    pygame.RESIZABLE | pygame.SCALED | pygame.DOUBLEBUF,
                    **display_kwargs
                )
            self.fullscreen = False
        else:
            windowed_size = screen.get_size()
            try:
                screen = pygame.display.set_mode(
                    (settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT),
                    pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF,
                    vsync=1,
                    **display_kwargs
                )
            except (pygame.error, TypeError):
                # Fallback to standard fullscreen if SCALED is unsupported.
                screen = pygame.display.set_mode(
                    (settings.DEFAULT_WINDOW_WIDTH, settings.DEFAULT_WINDOW_HEIGHT),
                    pygame.FULLSCREEN | pygame.DOUBLEBUF,
                    **display_kwargs
                )
            self.fullscreen = True

        # Resize first so scale-dependent assets recompute, then convert surfaces safely.
        settings.resize(*screen.get_size())  # Recompute sizes based on new window.
        settings._convert_surfaces_for_display(screen)
        main_menu._create_buttons()  # Recenter main menu buttons.
        self.refresh_layout()  # Recenter options buttons/slider.
        pause_menu._create_buttons()  # Recenter pause menu buttons.
        game_over_menu.refresh_layout()  # Recenter game over menu buttons.
        return screen, windowed_size


class PauseMenu:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        self.buttons = build_buttons(['Resume', 'Main Menu', 'Exit Game'], self.font, center_ratio=0.6)

    def draw(self, surface):
        bg = pygame.transform.scale(settings.PAUSED_IMAGE, surface.get_size())
        surface.blit(bg, (0, 0))

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "RESUME"

        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                if i == 0:
                    return "RESUME"
                if i == 1:
                    return "MAIN_MENU"
                if i == 2:
                    return "EXIT"
        return None


class GameOverMenu:
    def __init__(self, font):
        self.font = font
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        self.buttons = build_buttons(['Retry', 'Main Menu', 'Exit'], self.font, center_ratio=0.6)

    def draw(self, surface, score):
        bg = pygame.transform.scale(settings.MAIN_MENU_IMAGE, surface.get_size())
        surface.blit(bg, (0, 0))

        title = self.font.render('Game Over', True, 'white')
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() // 3))
        surface.blit(title, title_rect)

        score_text = self.font.render(f'Score: {score}', True, 'white')
        score_rect = score_text.get_rect(center=(surface.get_width() // 2, title_rect.bottom + 40))
        surface.blit(score_text, score_rect)

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "MAIN_MENU"

        for i, b in enumerate(self.buttons):
            if b.is_clicked(event):
                if i == 0:
                    return "RETRY"
                if i == 1:
                    return "MAIN_MENU"
                if i == 2:
                    return "EXIT"
        return None

    def refresh_layout(self):
        self._create_buttons()


def run_main_menu(screen, windowed_size, settings, main_menu, options_menu, pause_menu, game_over_menu, clock, on_fullscreen_toggled):
    """Main menu loop; exits when the user starts the game or quits."""
    pygame.mixer.music.stop()
    current_menu = "MAIN"  # Tracks whether we are in the main or options menu.
    while True:
        for event in pygame.event.get():  # Poll menu events.
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if current_menu == "MAIN":
                result = main_menu.handle_event(event)
                if result == 0:
                    return "START", screen, windowed_size
                elif result == 1:
                    current_menu = "OPTIONS"
                elif result == 2:
                    pygame.quit()
                    sys.exit()

            elif current_menu == "OPTIONS":
                result = options_menu.handle_event(event)

                if result == "TOGGLE_FULLSCREEN":
                    screen, windowed_size = options_menu.toggle_fullscreen(
                        screen, windowed_size, main_menu, pause_menu, game_over_menu
                    )
                    on_fullscreen_toggled()
                elif result == "BACK":
                    current_menu = "MAIN"

        if current_menu == "MAIN":
            main_menu.draw(screen)
        else:
            options_menu.draw(screen)

        pygame.display.update()
        clock.tick(settings.FPS)


def toggle_fullscreen(screen, windowed_size, options_menu, main_menu, pause_menu, game_over_menu, rebuild_static_layers):
    """Toggle fullscreen/windowed modes, refresh UI layout, and rebuild static layers."""
    screen, windowed_size = options_menu.toggle_fullscreen(
        screen, windowed_size, main_menu, pause_menu, game_over_menu
    )
    rebuild_static_layers()
    return screen, windowed_size


def show_main_menu(screen, windowed_size, settings, main_menu, options_menu, pause_menu, game_over_menu, clock, rebuild_static_layers):
    """
    Wrapper around run_main_menu for compatibility; returns (choice, screen, windowed_size).
    """
    return run_main_menu(
        screen,
        windowed_size,
        settings,
        main_menu,
        options_menu,
        pause_menu,
        game_over_menu,
        clock,
        rebuild_static_layers
    )
