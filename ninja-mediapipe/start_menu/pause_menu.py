# pause_menu.py
import pygame
from assets import load_background
from start_menu.ring_button import RingButtonCW as RingButton

def run_pause_menu(screen: pygame.Surface, clock: pygame.time.Clock,
                   *, bg_surface: pygame.Surface | None = None) -> str:
    """
    Hiển thị menu tạm dừng, trả về:
      - 'resume'  → tiếp tục chơi
      - 'restart' → chơi lại từ đầu
      - 'menu'    → quay lại menu chính
      - 'quit'    → thoát game
    """
    W, H = screen.get_width(), screen.get_height()

    # nền mờ
    bg = bg_surface or load_background((W, H))
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))

    # tạo nút
    cx, cy = W // 2, H // 2
    radius = 100
    gap = 260
    colors = [(60,160,255), (255,140,60), (240,70,70)]

    resume_btn = RingButton(center=(cx - gap, cy), radius=radius,
                            label="RESUME", ring_color=colors[0], glow_color=colors[0],
                            fruit_candidates=("watermelon.png","fruit_watermelon.png"),
                            fruit_fallback=(70,180,90))
    restart_btn = RingButton(center=(cx, cy), radius=radius,
                             label="RESTART", ring_color=colors[1], glow_color=colors[1],
                             fruit_candidates=("orange.png","fruit_orange.png"),
                             fruit_fallback=(255,160,60))
    menu_btn = RingButton(center=(cx + gap, cy), radius=radius,
                          label="BACK TO MENU", ring_color=colors[2], glow_color=colors[2],
                          fruit_candidates=("strawberry.png","fruit_strawberry.png"),
                          fruit_fallback=(230,80,80))
    buttons = [resume_btn, restart_btn, menu_btn]
    labels = ["resume", "restart", "menu"]
    focus = 0

    font = pygame.font.SysFont("Arial", 72, bold=True)
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_r): return "resume"
                if e.key in (pygame.K_LEFT, pygame.K_a): focus = (focus - 1) % len(buttons)
                if e.key in (pygame.K_RIGHT, pygame.K_d): focus = (focus + 1) % len(buttons)
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return labels[focus]
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                for i, b in enumerate(buttons):
                    if b.hit((mx, my)):
                        return labels[i]

        # vẽ nền
        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))
        txt = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(W//2, H//3)))

        # vẽ nút
        for i, b in enumerate(buttons):
            b.update(clock.get_time() / 1000)
            highlight = (i == focus) or b.hit(pygame.mouse.get_pos())
            b.draw(screen, highlight=highlight)

        pygame.display.flip()
        clock.tick(60)

    return "resume"
