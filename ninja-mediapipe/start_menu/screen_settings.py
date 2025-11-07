from __future__ import annotations
import pygame, os, math, time
from assets import load_background
from start_menu.config import MenuConfig
from start_menu.screens_basic import (
    _screen_howto, _screen_difficulty, _screen_hand, _screen_audio, _screen_scores
)
from start_menu.ring_button import RingButtonCW as RingButton

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets")

def _try_load_logo(max_box_size: int) -> pygame.Surface | None:
    for name in ("menu_logo.png", "menu_logo.jpg", "logo.png", "logo.jpg", "ptit_logo.png"):
        p = os.path.join(ASSETS_DIR, name)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                return pygame.transform.smoothscale(img, (max_box_size, max_box_size))
            except Exception:
                pass
    return None


def _grid_layout(W: int, H: int, rows: int, cols: int, radius: int, y_top_ratio=0.36):
    cx = W // 2
    total_w = (cols - 1) * radius * 2.6
    start_x = cx - total_w / 2
    y_top = int(H * y_top_ratio)
    gap_x = int(radius * 2.6)
    gap_y = int(radius * 2.4)
    centers = []
    for r in range(rows):
        y = y_top + r * gap_y
        for c in range(cols):
            x = int(start_x + c * gap_x)
            centers.append((x, y))
    return centers


def _make_setting_ring_buttons(W: int, H: int, radius: int = 90):
    centers = _grid_layout(W, H, rows=2, cols=3, radius=radius)
    BLUE       = (60, 160, 255)
    PURPLE     = (160, 90, 220)
    ORANGE     = (255, 140, 60)
    LIGHTGREEN = (140, 220, 120)
    DARKGREEN  = (40, 150, 80)
    RED        = (240, 70, 70)

    candidates = {
        "watermelon": ("fruit_watermelon.png", "watermelon.png", "melon.png", "fruit_melon.png"),
        "pineapple":  ("pineapple.png", "fruit_pineapple.png", "ananas.png"),
        "apple":      ("apple.png", "fruit_apple.png", "red_apple.png"),
        "banana":     ("banana.png", "fruit_banana.png"),
        "orange":     ("orange.png", "fruit_orange.png"),
        "strawberry": ("strawberry.png", "fruit_strawberry.png", "strawberry_icon.png"),
    }

    buttons = [
        RingButton(center=centers[0], radius=radius, label="HOW TO PLAY",
                   ring_color=BLUE, glow_color=BLUE,
                   fruit_candidates=candidates["watermelon"], fruit_fallback=(70, 180, 90),
                   speed_deg=36.0, density=0.95, word_gap=1, sep_spaces=4),
        RingButton(center=centers[1], radius=radius, label="HAND TRACKING",
                   ring_color=PURPLE, glow_color=PURPLE,
                   fruit_candidates=candidates["pineapple"], fruit_fallback=(230, 200, 60),
                   speed_deg=36.0, density=0.95, word_gap=1, sep_spaces=4),
        RingButton(center=centers[2], radius=radius, label="DIFFICULTY",
                   ring_color=ORANGE, glow_color=ORANGE,
                   fruit_candidates=candidates["apple"], fruit_fallback=(220, 60, 60),
                   speed_deg=36.0, density=1.05, word_gap=0, sep_spaces=3),
        RingButton(center=centers[3], radius=radius, label="HIGH SCORES",
                   ring_color=LIGHTGREEN, glow_color=LIGHTGREEN,
                   fruit_candidates=candidates["banana"], fruit_fallback=(230, 210, 70),
                   speed_deg=36.0, density=0.95, word_gap=1, sep_spaces=4),
        RingButton(center=centers[4], radius=radius, label="AUDIO",
                   ring_color=DARKGREEN, glow_color=DARKGREEN,
                   fruit_candidates=candidates["orange"], fruit_fallback=(255, 160, 60),
                   speed_deg=36.0, density=1.10, word_gap=0, sep_spaces=3),
        RingButton(center=centers[5], radius=radius, label="BACK",
                   ring_color=RED, glow_color=RED,
                   fruit_candidates=candidates["strawberry"], fruit_fallback=(230, 80, 80),
                   speed_deg=36.0, density=1.10, word_gap=0, sep_spaces=3),
    ]
    labels = ["howto", "hand", "difficulty", "scores", "audio", "back"]
    return buttons, labels


def _handle_subscreen(which: str, screen, clock, font, big_font, cfg: MenuConfig) -> str | None:
    """Chạy màn con. Luôn trả về 'back' để quay lại SETTINGS, hoặc 'quit' nếu đóng cửa sổ."""
    if which == "howto":      return _screen_howto(screen, clock, font, big_font)
    if which == "hand":       return _screen_hand(screen, clock, font, big_font, cfg)
    if which == "difficulty": return _screen_difficulty(screen, clock, font, big_font, cfg)
    if which == "scores":     return _screen_scores(screen, clock, font, big_font, None)
    if which == "audio":      return _screen_audio(screen, clock, font, big_font, cfg)
    return None


def _move_focus(index: int, cols: int, rows: int, key: int) -> int:
    r, c = divmod(index, cols)
    if key in (pygame.K_LEFT, pygame.K_a):  c = (c - 1) % cols
    elif key in (pygame.K_RIGHT, pygame.K_d): c = (c + 1) % cols
    elif key in (pygame.K_UP, pygame.K_w):   r = (r - 1) % rows
    elif key in (pygame.K_DOWN, pygame.K_s): r = (r + 1) % rows
    return r * cols + c


def _draw_stylized_title(screen, text: str, phase: float):
    """Vẽ title 'SETTINGS' có glow + gạch chân nhịp."""
    W = screen.get_width()
    # Shadow
    font_big = pygame.font.SysFont("Arial", 70, bold=True)
    surf = font_big.render(text, True, (255,255,255))
    rect = surf.get_rect(center=(W // 2, 108))

    # Glow (scale nhẹ + alpha)
    glow1 = pygame.transform.smoothscale(surf, (int(surf.get_width()*1.06), int(surf.get_height()*1.06)))
    glow2 = pygame.transform.smoothscale(surf, (int(surf.get_width()*1.12), int(surf.get_height()*1.12)))
    g1 = glow1.copy(); g1.fill((80,180,255,0), special_flags=pygame.BLEND_RGBA_MULT)
    g2 = glow2.copy(); g2.fill((80,180,255,0), special_flags=pygame.BLEND_RGBA_MULT)
    g1.set_alpha(90); g2.set_alpha(50)
    screen.blit(g2, g2.get_rect(center=rect.center))
    screen.blit(g1, g1.get_rect(center=rect.center))

    # Main text
    screen.blit(surf, rect)

    # Underline pulse
    bar_w = int(surf.get_width() * (0.65 + 0.15*math.sin(phase*2.0)))
    bar_h = 8
    bar = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    pygame.draw.rect(bar, (80,180,255,200), (0,0,bar_w,bar_h), border_radius=6)
    screen.blit(bar, (rect.centerx - bar_w//2, rect.bottom + 6))


def _draw_hint(screen):
    info_font = pygame.font.SysFont("Consolas", 22)
    txt = "Arrows/WASD move • Enter/Space select • Esc = Back to START • In sub-screens: Esc/B/Enter/Space = Back to SETTINGS"
    surf = info_font.render(txt, True, (210, 210, 210))
    screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 36)))


def _screen_settings(screen, clock, font, big_font, cfg: MenuConfig):
    W, H = screen.get_width(), screen.get_height()
    try:
        bg = load_background(
            (W, H),
            names=("settings_background.jpg","settings_background.png","settings_bg.jpg","settings_bg.png",
                   "menu_background.jpg","menu_background.png","menu_bg.jpg","menu_bg.png",
                   "background.jpg","background.png","bg.jpg","bg.png"))
    except TypeError:
        bg = load_background((W, H))

    # 6 nút ring
    buttons, labels = _make_setting_ring_buttons(W, H, radius=92)
    cols, rows = 3, 2
    focus = 0

    # logo PTIT = Back to Start
    logo_size = 56
    logo_pad = 16
    logo = _try_load_logo(logo_size)
    logo_rect = pygame.Rect(logo_pad, logo_pad, logo_size, logo_size)

    # phase cho hiệu ứng tiêu đề
    t0 = time.perf_counter()

    while True:
        dt = clock.get_time() / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:  # Esc tại CHÍNH màn SETTINGS => về START
                    return "back"
                if e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                             pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
                    focus = _move_focus(focus, cols, rows, e.key)
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    which = labels[focus]
                    if which == "back":
                        return "back"   # nút BACK (vòng đỏ) => rời SETTINGS về START
                    # Màn con: chỉ quay lại SETTINGS khi xong
                    res = _handle_subscreen(which, screen, clock, font, big_font, cfg)
                    if res == "quit": return "quit"
                    # res == "back" => tiếp tục vòng while, vẫn ở SETTINGS
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # click logo → về Start
                if logo_rect.collidepoint(mx, my): return "back"
                # click các ring
                for i, b in enumerate(buttons):
                    if b.hit((mx, my)):
                        focus = i
                        which = labels[i]
                        if which == "back":
                            return "back"
                        res = _handle_subscreen(which, screen, clock, font, big_font, cfg)
                        if res == "quit": return "quit"
                        break

        # update
        for b in buttons: b.update(dt)

        # draw
        screen.blit(bg, (0, 0))
        phase = time.perf_counter() - t0
        _draw_stylized_title(screen, "SETTINGS", phase)

        mouse = pygame.mouse.get_pos()
        for i, b in enumerate(buttons):
            highlight = (i == focus) or b.hit(mouse)
            b.draw(screen, highlight=highlight)

        # vẽ logo back (góc trái trên)
        if logo:
            if logo_rect.collidepoint(mouse):
                s = pygame.Surface((logo_size+12, logo_size+12), pygame.SRCALPHA)
                pygame.draw.circle(s, (255,255,255,26), (s.get_width()//2, s.get_height()//2), (logo_size+10)//2)
                screen.blit(s, (logo_rect.x-6, logo_rect.y-6))
            screen.blit(logo, (logo_rect.x, logo_rect.y))
        else:
            # fallback: mũi tên
            pygame.draw.polygon(screen, (235,235,235),
                                [(logo_rect.x+logo_size*0.75, logo_rect.y+logo_size*0.2),
                                 (logo_rect.x+logo_size*0.25, logo_rect.y+logo_size*0.5),
                                 (logo_rect.x+logo_size*0.75, logo_rect.y+logo_size*0.8)], width=0)

        _draw_hint(screen)
        pygame.display.flip()
        clock.tick(60)
