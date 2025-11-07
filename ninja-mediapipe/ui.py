# ui.py
import pygame

def draw_text(surf, text, pos, color=(255,255,255), size=36, center=False):
    font = pygame.font.SysFont("Arial", size)
    txt = font.render(text, True, color)
    if center:
        rect = txt.get_rect(center=pos)
        surf.blit(txt, rect)
    else:
        surf.blit(txt, pos)

def draw_button(surface, rect, label, hover_color, normal_color, font_size=36):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    bg = hover_color if is_hover else normal_color
    pygame.draw.rect(surface, bg, rect, border_radius=12)
    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=12)
    font_local = pygame.font.SysFont("Arial", font_size)
    label_surf = font_local.render(label, True, (255, 255, 255))
    surface.blit(label_surf, label_surf.get_rect(center=rect.center))
    return is_hover
