from __future__ import annotations
import pygame
from assets import load_background
from start_menu.ring_button import RingButtonCW as RingButton

def _make_buttons(W: int, H: int, radius: int = 110):
    cx, cy = W // 2, int(H * 0.55)
    gap_x = int(radius * 2.6)

    RED  = (240, 70, 70)
    BLUE = (60, 160, 255)

    strawberry_candidates = ("strawberry.png", "fruit_strawberry.png", "strawberry_icon.png")
    watermelon_candidates = ("fruit_watermelon.png", "watermelon.png", "melon.png", "fruit_melon.png")

    back_btn = RingButton(
        center=(cx - gap_x // 2, cy),
        radius=radius,
        label="BACK TO MENU",
        ring_color=RED, glow_color=RED,
        fruit_candidates=strawberry_candidates, fruit_fallback=(230, 80, 80),
        speed_deg=36.0,
        # lặp đúng 3 lần
        density=1.0, word_gap=1, sep_spaces=4, min_repeat=3, max_repeat=3
    )
    again_btn = RingButton(
        center=(cx + gap_x // 2, cy),
        radius=radius,
        label="PLAY AGAIN",
        ring_color=BLUE, glow_color=BLUE,
        fruit_candidates=watermelon_candidates, fruit_fallback=(70, 180, 90),
        speed_deg=36.0,
        # lặp đúng 4 lần
        density=1.0, word_gap=1, sep_spaces=4, min_repeat=4, max_repeat=4
    )

    return [back_btn, again_btn], ["back_to_menu", "play_again"]


def _draw_title(screen: pygame.Surface, text: str = "GAME OVER"):
    big_font = pygame.font.SysFont("Arial", 72, bold=True)
    surf = big_font.render(text, True, (255, 255, 255))
    screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, int(screen.get_height() * 0.28))))


def _draw_hint(screen: pygame.Surface):
    info = pygame.font.SysFont("Consolas", 22)
    txt = "Arrows/WASD move  •  Enter/Space select  •  Esc to go back"
    surf = info.render(txt, True, (210, 210, 210))
    screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 36)))


def run_game_over_menu(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    *,
    bg_surface: pygame.Surface | None = None,
    background_names: tuple[str, ...] = (
        "gameover_background.jpg","gameover_background.png",
        "menu_background.jpg","menu_background.png",
        "background.jpg","background.png","bg.jpg","bg.png"
    ),
    title_text: str = "GAME OVER",
) -> str:
    """
    Hiển thị menu sau khi chơi xong, trả về:
      - 'back_to_menu' khi chọn Back to Menu hoặc nhấn Esc
      - 'play_again'  khi chọn Play Again
      - 'quit'        nếu người dùng đóng cửa sổ

    bg_surface: nếu truyền vào (từ game), sẽ dùng CHÍNH background đó (đã đúng size).
    """
    W, H = screen.get_width(), screen.get_height()

    # dùng background truyền vào từ game nếu có
    if bg_surface is not None:
        bg = bg_surface
    else:
        try:
            bg = load_background((W, H), names=background_names)
        except TypeError:
            bg = load_background((W, H))

    buttons, labels = _make_buttons(W, H, radius=110)
    focus = 0

    running = True
    while running:
        dt = clock.get_time() / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "back_to_menu"
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    focus = (focus - 1) % len(buttons)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    focus = (focus + 1) % len(buttons)
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return labels[focus]
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                for i, b in enumerate(buttons):
                    if b.hit((mx, my)):
                        focus = i
                        return labels[i]

        # Draw background + overlay mờ
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        _draw_title(screen, title_text)

        # Update + Draw buttons
        for b in buttons:
            b.update(dt)

        mouse = pygame.mouse.get_pos()
        for i, b in enumerate(buttons):
            highlight = (i == focus) or b.hit(mouse)
            b.draw(screen, highlight=highlight)

        _draw_hint(screen)
        pygame.display.flip()
        clock.tick(60)

    return "back_to_menu"
