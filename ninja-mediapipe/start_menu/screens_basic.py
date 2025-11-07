from __future__ import annotations
import pygame, os
from assets import load_background

# path to assets folder (relative to this module)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets")


def _try_load_background_set(size: tuple[int, int]) -> pygame.Surface | None:
    """Only load background_set.(jpg|png) from assets if present. Return surface or None."""
    W, H = size
    for name in ("background_set.jpg", "background_set.png"):
        p = os.path.join(ASSETS_DIR, name)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                return pygame.transform.smoothscale(img, (W, H))
            except Exception:
                return None
    return None


def _back_button_rect(screen: pygame.Surface) -> pygame.Rect:
    """Compute the undo/back button rectangle near the top-left corner."""
    w, h = screen.get_width(), screen.get_height()
    size = max(56, min(88, int(min(w, h) * 0.12)))
    margin_x = max(24, int(size * 0.45))
    margin_y = max(20, int(size * 0.35))
    return pygame.Rect(margin_x, margin_y, size, size)


def _draw_back_button(screen: pygame.Surface, rect: pygame.Rect, hover: bool) -> None:
    """Draw a simple undo-style back button."""
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    center = (rect.width // 2, rect.height // 2)
    radius = min(rect.width, rect.height) // 2

    if hover:
        pygame.draw.circle(surf, (70, 150, 255, 90), center, radius)
    pygame.draw.circle(surf, (18, 24, 32, 230), center, radius - 3)

    ring_color = (255, 255, 255, 230) if hover else (220, 220, 220, 190)
    pygame.draw.circle(surf, ring_color, center, radius - 3, width=3)

    arrow_color = (255, 255, 255, 240) if hover else (220, 225, 230, 220)
    thickness = max(4, rect.width // 10)
    left = int(rect.width * 0.30)
    shaft_right = int(rect.width * 0.70)
    tip_top = int(rect.height * 0.30)
    tip_bottom = int(rect.height * 0.70)
    mid_y = center[1]

    pygame.draw.line(surf, arrow_color, (shaft_right, mid_y), (left, mid_y), thickness)
    pygame.draw.line(surf, arrow_color, (left, mid_y), (int(rect.width * 0.52), tip_top), thickness)
    pygame.draw.line(surf, arrow_color, (left, mid_y), (int(rect.width * 0.52), tip_bottom), thickness)

    screen.blit(surf, rect.topleft)

# === HOW TO ===
def _screen_howto(screen, clock, font, big_font):
    mono = pygame.font.SysFont("Consolas", 24)
    lines = [
        "HOW TO PLAY",
        "- Move your index fingertip in front of the camera to control the blade.",
        "- Slice fruits to score; avoid bombs.",
        "- Combo: slice multiple fruits within < 1s to get extra points.",
        "- Click the undo icon in the top-left or press Esc / B to return.",
    ]
    W, H = screen.get_width(), screen.get_height()
    # Prefer only background_set.* if present
    bg = _try_load_background_set((W, H))

    while True:
        back_rect = _back_button_rect(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_rect.collidepoint(e.pos): return "back"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_b):
                    return "back"  # QUAY LẠI SETTINGS
        # draw background (if available) then content on top
        if bg is not None:
            screen.blit(bg, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((10,10,15))
        title_surf = big_font.render(lines[0], True, (255,255,255))
        screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width()//2, 90)))
        y = 160
        for line in lines[1:]:
            txt = font.render(line, True, (220,220,220))
            screen.blit(txt, (60, y)); y += 48
        hint = mono.render("[Esc/B/Enter/Space] Back to SETTINGS   |   Click undo icon", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, screen.get_height()-40)))
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        _draw_back_button(screen, back_rect, hover)
        pygame.display.flip(); clock.tick(60)


# === DIFFICULTY ===

def _screen_difficulty(screen, clock, font, big_font, cfg):
    options = ["Easy", "Normal", "Hard"]
    idx = options.index(cfg.difficulty) if cfg.difficulty in options else 1
    info_font = pygame.font.SysFont("Consolas", 24)
    W, H = screen.get_width(), screen.get_height()
    # Prefer only background_set.* if present
    bg = _try_load_background_set((W, H))

    while True:
        back_rect = _back_button_rect(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_b):
                    return "back"  # QUAY LAI SETTINGS
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    idx = (idx - 1) % len(options)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    idx = (idx + 1) % len(options)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_rect.collidepoint(e.pos):
                    return "back"
                mx, my = e.pos
                if screen.get_height()//2 - 40 < my < screen.get_height()//2 + 40:
                    idx = (idx + (1 if mx > screen.get_width()//2 else -1)) % len(options)

        # Apply difficulty selection to the menu config
        name = options[idx].title()
        if name == "Easy":
            cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Easy", 1.8, 0.10, 0.30, 3
        elif name == "Hard":
            cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Hard", 1.0, 0.22, 0.40, 2
        else:
            cfg.difficulty, cfg.fruit_interval, cfg.bomb_rate, cfg.gravity, cfg.max_lives = "Normal", 1.4, 0.15, 0.35, 3

        if bg is not None:
            screen.blit(bg, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((12,12,18))
        title = big_font.render("DIFFICULTY", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 90)))
        label = big_font.render(cfg.difficulty, True, (255,220,120))
        screen.blit(label, label.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
        lines = [
            f"Fruit interval: {cfg.fruit_interval:.2f}s",
            f"Bomb rate: {int(cfg.bomb_rate*100)}%",
            f"Gravity: {cfg.gravity:.2f}",
            f"Max lives: {cfg.max_lives}",
        ]
        y = screen.get_height()//2 + 70
        for t in lines:
            txt = info_font.render(t, True, (220,220,220))
            screen.blit(txt, txt.get_rect(center=(screen.get_width()//2, y)))
            y += 30
        hint = info_font.render("[Left/Right] Change  |  [Enter/Space] Back  |  [Esc/B or Undo] Back to SETTINGS", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, screen.get_height()-40)))
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        _draw_back_button(screen, back_rect, hover)
        pygame.display.flip()
        clock.tick(60)



# === HAND ===

def _screen_hand(screen, clock, font, big_font, cfg):
    items = ["Enabled", "Preview", "Camera Index"]
    cur = 0
    info_font = pygame.font.SysFont("Consolas", 24)

    def draw_row(i, label, value):
        y = 200 + i*70
        selected = (i == cur)
        color = (255,255,255) if selected else (200,200,200)
        value_color = (255,220,120) if selected else (180,160,120)
        l_surf = font.render(label, True, color)
        v_surf = font.render(str(value), True, value_color)
        screen.blit(l_surf, (160, y))
        screen.blit(v_surf, v_surf.get_rect(right=screen.get_width()-160, y=y))

    W, H = screen.get_width(), screen.get_height()
    bg = _try_load_background_set((W, H))

    while True:
        back_rect = _back_button_rect(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_RETURN, pygame.K_SPACE):
                    return "back"  # QUAY LAI SETTINGS
                if e.key in (pygame.K_UP, pygame.K_w):
                    cur = (cur - 1) % len(items)
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    cur = (cur + 1) % len(items)
                if e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE, pygame.K_RETURN):
                    if cur == 0:
                        cfg.hand_enabled = not cfg.hand_enabled
                    elif cur == 1:
                        cfg.hand_preview = not cfg.hand_preview
                    else:
                        if e.key in (pygame.K_LEFT, pygame.K_a):
                            cfg.camera_index = max(0, cfg.camera_index - 1)
                        elif e.key in (pygame.K_RIGHT, pygame.K_d):
                            cfg.camera_index += 1
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_rect.collidepoint(e.pos):
                    return "back"

        if bg is not None:
            screen.blit(bg, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((10,14,20))
        title = big_font.render("HAND TRACKING", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 90)))
        draw_row(0, "Enabled", "ON" if cfg.hand_enabled else "OFF")
        draw_row(1, "Preview", "ON" if cfg.hand_preview else "OFF")
        draw_row(2, "Camera Index", cfg.camera_index)
        hint = info_font.render("[W/S] Move  |  [A/D/Space/Enter] Toggle  |  [Esc/B or Undo] Back to SETTINGS", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, screen.get_height()-40)))
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        _draw_back_button(screen, back_rect, hover)
        pygame.display.flip()
        clock.tick(60)



# === AUDIO ===

def _screen_audio(screen, clock, font, big_font, cfg):
    cur = 0
    info_font = pygame.font.SysFont("Consolas", 24)

    def clamp(x, lo=0.0, hi=1.0):
        return max(lo, min(hi, x))

    def draw_slider(y, value: float, label: str, selected: bool):
        bar_w, bar_h = 520, 10
        cx = screen.get_width()//2
        x = cx - bar_w//2
        color = (255,255,255) if selected else (200,200,200)
        lab = font.render(f"{label}: {int(value*100)}%", True, color)
        screen.blit(lab, lab.get_rect(center=(cx, y-26)))
        pygame.draw.rect(screen, (80,80,90), (x, y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * value)
        pygame.draw.rect(screen, (60,160,220), (x, y, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, (230,230,230), (x, y, bar_w, bar_h), 2, border_radius=6)

    W, H = screen.get_width(), screen.get_height()
    bg = _try_load_background_set((W, H))

    while True:
        back_rect = _back_button_rect(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_RETURN, pygame.K_SPACE):
                    return "back"  # QUAY LAI SETTINGS
                if e.key in (pygame.K_UP, pygame.K_w):
                    cur = (cur - 1) % 2
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    cur = (cur + 1) % 2
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    if cur == 0:
                        cfg.music_volume = clamp(cfg.music_volume - 0.05)
                    else:
                        cfg.sfx_volume = clamp(cfg.sfx_volume - 0.05)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    if cur == 0:
                        cfg.music_volume = clamp(cfg.music_volume + 0.05)
                    else:
                        cfg.sfx_volume = clamp(cfg.sfx_volume + 0.05)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_rect.collidepoint(e.pos):
                    return "back"

        if bg is not None:
            screen.blit(bg, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((14,10,18))
        title = big_font.render("AUDIO", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 90)))
        draw_slider(250, cfg.music_volume, "Music Volume", cur == 0)
        draw_slider(360, cfg.sfx_volume, "SFX Volume", cur == 1)
        hint = info_font.render("[W/S] Select  |  [A/D] Adjust  |  [Esc/B/Enter/Space or Undo] Back to SETTINGS", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, screen.get_height()-40)))
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        _draw_back_button(screen, back_rect, hover)
        pygame.display.flip()
        clock.tick(60)



# === HIGH SCORES ===

def _screen_scores(screen, clock, font, big_font, best_score_val: int | None = None):
    import datetime
    head_font = pygame.font.SysFont("Consolas", 28, bold=True)
    row_font = pygame.font.SysFont("Consolas", 26)
    info_font = pygame.font.SysFont("Consolas", 22)
    W, H = screen.get_width(), screen.get_height()
    x_rank, x_name_left, x_score_right, x_diff_center, x_date_right = 100, 180, W-420, W-270, W-40
    name_max_width = (x_score_right - 40) - x_name_left

    def draw_center(text, y, *, color=(230,230,230), font_obj=row_font, centerx=None):
        surf = font_obj.render(text, True, color)
        rect = surf.get_rect(center=(centerx, y))
        screen.blit(surf, rect)

    def draw_left(text, y, x, *, color=(230,230,230), font_obj=row_font):
        surf = font_obj.render(text, True, color)
        rect = surf.get_rect(topleft=(x, y - surf.get_height()//2))
        screen.blit(surf, rect)

    def draw_right(text, y, right_x, *, color=(230,230,230), font_obj=row_font):
        surf = font_obj.render(text, True, color)
        rect = surf.get_rect(midright=(right_x, y))
        screen.blit(surf, rect)

    def truncate_to_width(text, max_w, font_obj=row_font):
        if font_obj.size(text)[0] <= max_w:
            return text
        ell = "..."
        s = text
        while s and font_obj.size(s + ell)[0] > max_w:
            s = s[:-1]
        return (s + ell) if s else ell

    import highscores as hs
    rows = hs.get_top(20)
    sel = 0

    bg = _try_load_background_set((W, H))

    while True:
        back_rect = _back_button_rect(screen)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_RETURN, pygame.K_SPACE):
                    return "back"  # QUAY LAI SETTINGS
                if e.key in (pygame.K_UP, pygame.K_w) and rows:
                    sel = (sel - 1) % len(rows)
                if e.key in (pygame.K_DOWN, pygame.K_s) and rows:
                    sel = (sel + 1) % len(rows)
                if rows and (e.key == pygame.K_d or e.key == pygame.K_DELETE):
                    hs.delete_by_rank(sel + 1)
                    rows = hs.get_top(20)
                    sel = min(sel, max(0, len(rows) - 1))
                if e.key == pygame.K_r:
                    hs.reset_scores()
                    rows = hs.get_top(20)
                    sel = 0
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_rect.collidepoint(e.pos):
                    return "back"

        if bg is not None:
            screen.blit(bg, (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((10,10,10))
        title = big_font.render("HIGH SCORES", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(W//2, 90)))
        header_y = 150
        draw_center("RANK", header_y, color=(200,220,255), font_obj=head_font, centerx=x_rank)
        draw_left("NAME", header_y, x_name_left, color=(200,220,255), font_obj=head_font)
        draw_right("SCORE (norm)", header_y, x_score_right, color=(200,220,255), font_obj=head_font)
        draw_center("DIFF", header_y, color=(200,220,255), font_obj=head_font, centerx=x_diff_center)
        draw_right("DATE", header_y, x_date_right, color=(200,220,255), font_obj=head_font)
        pygame.draw.line(screen, (80,80,90), (60, header_y+16), (W-60, header_y+16), 2)

        base_y = header_y + 50
        row_h = 40
        if not rows:
            txt = info_font.render("No scores yet. Play to set a new record!", True, (220,220,220))
            screen.blit(txt, txt.get_rect(center=(W//2, base_y + 20)))
        else:
            for i, it in enumerate(rows, start=1):
                y = base_y + (i-1) * row_h
                nm = truncate_to_width(str(it.get("name", "PLAYER")), name_max_width, row_font)
                raw_score = int(it.get("score", 0))
                scr = int(round(float(it.get("norm", raw_score))))
                diff = str(it.get("difficulty", "N/A"))
                ts = it.get("ts")
                if isinstance(ts, (int, float)):
                    date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts) if ts else ""
                color = (255,215,0) if i == 1 else (230,230,230)
                if (i - 1) == sel:
                    hi = pygame.Surface((W-120, row_h), pygame.SRCALPHA)
                    hi.fill((255,255,255,30))
                    screen.blit(hi, (60, y - row_h//2))
                draw_center(f"{i:>2}", y, color=color, centerx=x_rank)
                draw_left(nm, y, x_name_left, color=color)
                draw_right(f"{scr}", y, x_score_right, color=color)
                draw_center(diff, y, color=color, centerx=x_diff_center)
                draw_right(date_str, y, x_date_right, color=color)

        hint = info_font.render("[Up/Down] Select  |  [D/Delete] Remove  |  [R] Reset  |  [Esc/B/Enter/Space or Undo] Back to SETTINGS", True, (210,210,210))
        screen.blit(hint, hint.get_rect(center=(W//2, H-30)))
        hover = back_rect.collidepoint(pygame.mouse.get_pos())
        _draw_back_button(screen, back_rect, hover)
        pygame.display.flip()
        clock.tick(60)

