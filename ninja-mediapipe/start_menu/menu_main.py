import pygame, os, math, time
from dataclasses import asdict
from assets import load_background
from start_menu.config import MenuConfig
from start_menu.screen_settings import _screen_settings

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets")

# ==========================================================
# Helpers for logo / gear icon
# ==========================================================
def _try_load_logo(max_box_size: int) -> pygame.Surface | None:
    """Tìm file logo trong thư mục assets."""
    for name in ("menu_logo.png", "menu_logo.jpg", "logo.png", "logo.jpg", "ptit_logo.png"):
        p = os.path.join(ASSETS_DIR, name)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                return pygame.transform.smoothscale(img, (max_box_size, max_box_size))
            except Exception:
                pass
    return None

def _draw_gear_icon(surf: pygame.Surface, center: tuple[int,int], radius: int, *, color=(235,235,235), hover=False):
    """Fallback: bánh răng thay cho logo."""
    x, y = center
    if hover:
        pygame.draw.circle(surf, (255,255,255,26), center, radius+10)
    teeth = 8; inner = int(radius * 0.55)
    for i in range(teeth):
        ang = (i / teeth) * 360
        rect = pygame.Surface((int(radius*0.55), int(radius*0.25)), pygame.SRCALPHA)
        pygame.draw.rect(rect, color, rect.get_rect(), border_radius=6)
        rot = pygame.transform.rotate(rect, ang)
        surf.blit(rot, (x - rot.get_width()//2, y - radius + 2))
    pygame.draw.circle(surf, color, center, int(radius*0.85), width=3)
    pygame.draw.circle(surf, color, center, inner, width=3)

# ==========================================================
# RingButton class (fixed text direction)
# ==========================================================
class RingButton:
    def __init__(self, center, radius, label, *,
                 ring_color=(60,160,220), glow_color=(60,160,220),
                 fruit_candidates=(), fruit_fallback=(220,220,220),
                 font_name="Consolas", text_speed=30.0, fruit_speed=-30.0):
        self.cx, self.cy = center; self.r = radius
        self.label = label
        self.ring_color, self.glow_color = ring_color, glow_color
        self.font = pygame.font.SysFont(font_name, max(22, radius//5), bold=True)
        self.text_speed = text_speed
        self.fruit_speed = fruit_speed
        self.text_angle = 0.0
        self.fruit_angle = 0.0

        fruit = None
        for name in fruit_candidates:
            p = os.path.join(ASSETS_DIR, name)
            if os.path.exists(p):
                fruit = pygame.image.load(p).convert_alpha()
                break
        if fruit is None:
            fruit = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(fruit, fruit_fallback, (radius, radius), int(radius*0.7))
        self.fruit_img = pygame.transform.smoothscale(fruit, (int(radius*1.25), int(radius*1.25)))
        self._ring_base = self._make_ring_graphics(radius, ring_color, glow_color)

    def _make_ring_graphics(self, radius, ring_color, glow_color):
        size = radius*2 + 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        outer = radius
        inner = int(radius*0.6)
        for i in range(8, 0, -1):
            a = max(8, int(18*i))
            pygame.draw.circle(surf, (*glow_color, a), center, outer + i*2, width=8)
        pygame.draw.circle(surf, (*ring_color, 220), center, outer, width=16)
        pygame.draw.circle(surf, (255,255,255,180), center, outer, width=3)
        pygame.draw.circle(surf, (0,0,0,40), center, inner, width=3)
        return surf

    def _draw_ring_text_once(self, target, angle_deg):
        # FIXED DIRECTION HERE ⬇️
        text = (self.label + "   ") * 6
        R = int(self.r * 0.86)
        step = 360 / max(1, len(text))
        for i, ch in enumerate(text):
            theta = math.radians(angle_deg - i*step)  # đảo dấu để chữ xoay thuận
            x = self.cx + R * math.cos(theta)
            y = self.cy + R * math.sin(theta)
            rot = math.degrees(theta) - 90  # xoay chữ đúng hướng đọc
            glyph = self.font.render(ch, True, (255,255,255))
            glyph = pygame.transform.rotozoom(glyph, rot, 1.0)
            target.blit(glyph, glyph.get_rect(center=(x, y)))

    def update(self, dt):
        self.text_angle = (self.text_angle + self.text_speed * dt) % 360.0
        self.fruit_angle = (self.fruit_angle + self.fruit_speed * dt) % 360.0

    def draw(self, screen, highlight=False):
        ring_rect = self._ring_base.get_rect(center=(self.cx, self.cy))
        screen.blit(self._ring_base, ring_rect)
        self._draw_ring_text_once(screen, self.text_angle)
        rotated = pygame.transform.rotozoom(self.fruit_img, self.fruit_angle, 1.0)
        fr = rotated.get_rect(center=(self.cx, self.cy))
        screen.blit(rotated, fr)
        if highlight:
            s = pygame.Surface((self.r*2+10, self.r*2+10), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255,30), (s.get_width()//2, s.get_height()//2), self.r+5)
            screen.blit(s, (self.cx - s.get_width()//2, self.cy - s.get_height()//2))

    def hit(self, pos):
        mx, my = pos
        return (mx - self.cx)**2 + (my - self.cy)**2 <= (self.r*0.95)**2

# ==========================================================
# MAIN MENU
# ==========================================================
def run_menu(screen=None, clock=None, *, title="Main Menu",
             initial=None, best_score=None) -> tuple[str, MenuConfig]:

    owns_pygame = False
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption(title)
        owns_pygame = True
    if clock is None:
        clock = pygame.time.Clock()

    try:
        menu_bg = load_background(
            (screen.get_width(), screen.get_height()),
            names=("menu_background.jpg","menu_background.png","background.jpg","bg.png")
        )
    except TypeError:
        menu_bg = load_background((screen.get_width(), screen.get_height()))

    cfg = MenuConfig() if initial is None else initial
    font = pygame.font.SysFont("Arial", 36)
    big_font = pygame.font.SysFont("Arial", 64, bold=True)
    small = pygame.font.SysFont("Consolas", 22)

    W, H = screen.get_width(), screen.get_height()
    cx = W // 2
    base_y = int(H * 0.52)
    gap_x = 280

    start_btn = RingButton(
        center=(cx - gap_x//2, base_y), radius=110, label="START",
        ring_color=(60,160,255), glow_color=(60,160,255),
        fruit_candidates=("fruit_watermelon.png","watermelon.png","melon.png","fruit_melon.png"),
        fruit_fallback=(70,180,90)
    )
    quit_btn = RingButton(
        center=(cx + gap_x//2, base_y), radius=110, label="QUIT",
        ring_color=(240,70,70), glow_color=(240,70,70),
        fruit_candidates=("strawberry.png","fruit_strawberry.png","strawberry_icon.png"),
        fruit_fallback=(230,80,80)
    )
    buttons = [start_btn, quit_btn]
    focus = 0

    gear_padding = 16
    box_size = 56
    gear_center = (W - (28 + gear_padding), 28 + gear_padding)
    logo_surf = _try_load_logo(box_size)

    _best = best_score
    _best_text = f"BEST (normalized): {int(_best)}" if _best is not None else "BEST: N/A"

    running = True
    action = None
    prev_time = time.perf_counter()

    while running:
        now = time.perf_counter()
        dt = now - prev_time
        prev_time = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                action = "quit"; running = False; break
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    action = "quit"; running = False; break
                if e.key in (pygame.K_LEFT, pygame.K_a):  focus = (focus - 1) % len(buttons)
                if e.key in (pygame.K_RIGHT, pygame.K_d): focus = (focus + 1) % len(buttons)
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    pos = (buttons[focus].cx, buttons[focus].cy)
                    e = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
                if e.key == pygame.K_o:
                    if _screen_settings(screen, clock, font, big_font, cfg) == "quit":
                        action = "quit"; running = False; break
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if start_btn.hit(e.pos):
                    action = "start"; running = False; break
                elif quit_btn.hit(e.pos):
                    action = "quit"; running = False; break
                elif (W - box_size - gear_padding) <= e.pos[0] <= (W - gear_padding) and gear_padding <= e.pos[1] <= (gear_padding + box_size):
                    if _screen_settings(screen, clock, font, big_font, cfg) == "quit":
                        action = "quit"; running = False; break

        for b in buttons:
            b.update(dt)

        screen.blit(menu_bg, (0, 0))
        mouse = pygame.mouse.get_pos()
        start_btn.draw(screen, highlight=start_btn.hit(mouse) or focus == 0)
        quit_btn.draw(screen, highlight=quit_btn.hit(mouse) or focus == 1)

        footer = (f"{cfg.difficulty} | Interval {cfg.fruit_interval:.2f}s | "
                  f"Bomb {int(cfg.bomb_rate*100)}% | Lives {cfg.max_lives} | "
                  f"Hand {'ON' if cfg.hand_enabled else 'OFF'}(cam {cfg.camera_index}) | "
                  f"Music {int(cfg.music_volume*100)}% | SFX {int(cfg.sfx_volume*100)}%")
        foot_surf = small.render(footer, True, (220,220,220))
        screen.blit(foot_surf, foot_surf.get_rect(center=(cx, H-28)))

        best_surf = small.render(_best_text, True, (235,235,235))
        screen.blit(best_surf, (16, 16))

        hover = pygame.Rect(W - box_size - gear_padding, gear_padding, box_size, box_size).collidepoint(mouse)
        if logo_surf:
            if hover:
                s = pygame.Surface((box_size+12, box_size+12), pygame.SRCALPHA)
                pygame.draw.circle(s, (255,255,255,26), (s.get_width()//2, s.get_height()//2), (box_size+10)//2)
                screen.blit(s, (W - box_size - gear_padding - 6, gear_padding - 6))
            screen.blit(logo_surf, (W - box_size - gear_padding, gear_padding))
        else:
            _draw_gear_icon(screen, gear_center, radius=22, color=(235,235,235), hover=hover)

        pygame.display.flip()
        clock.tick(60)

    if owns_pygame:
        pygame.quit()
    return (action or "quit", cfg)
