from global_variables import *
import cv2
import sys
import random
import pygame
import numpy as np
import json
import os
import global_variables as gv
from pygame.locals import *

def difficultyMenu():
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * gv.SCALE_FACTOR), bold=True)  # FIX: DejaVuSans + scale cho UTF-8 Anh/Việt nếu cần
    small_font = pygame.font.SysFont('dejavusans', int(25 * gv.SCALE_FACTOR))  # FIX: Scale nhỏ hơn cho levels

    selected = 0
    levels = list(gv.DIFFICULTY_LEVELS.keys())  # ['Easy', 'Medium', 'Hard']
    button_rects = []  # Tạo list khung button cho menu
    hover_index = -1 

    while True:
        mouse_pos = pygame.mouse.get_pos()  # FIX: Lấy vị trí chuột mỗi frame cho hover
        angles = [None]  #Gesture đơn giản cho menu (1 tay)

        # Gesture (tùy chọn, nếu cap) 
        if gv.cap:
            ret, img = gv.cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = gv.hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])  # Trung bình góc tay
                gv.hand.draw2d(img, param)
                cv2.imshow('Hand', img)  # Window debug gesture
                cv2.waitKey(1)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gv.MENU_STATE = 'main'  # Quay về main menu
                return
            elif event.type == KEYDOWN:
                # FIX: UP/DOWN + gesture (thả tay >55 = UP, nắm <30 = DOWN)
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected = (selected - 1) % len(levels)
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected = (selected + 1) % len(levels)
                elif event.key == K_RETURN:
                    gv.current_difficulty = levels[selected]
                    gv.MENU_STATE = 'playing'
                    return  # Bắt đầu mainGame
            elif event.type == MOUSEMOTION:  # FIX: Hover effect như mainMenu
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                else:
                    hover_index = -1
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # FIX: Click button
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        gv.current_difficulty = levels[i]
                        gv.MENU_STATE = 'playing'
                        return

        # Vẽ submenu – Giống mainMenu, background + title English
        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))
        title = font.render('Select Difficulty', True, (255, 255, 255))  # FIX: English
        gv.SCREEN.blit(title, (gv.SCREENWIDTH // 2 - title.get_width() // 2, 100))

        button_rects = []  # FIX: Reset mỗi frame
        for i, level in enumerate(levels):  # FIX: Loop vẽ button cho mỗi level
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 215, 0) if is_hover else (255, 255, 0) if is_selected else (255, 255, 255)  # FIX: Color như mainMenu
            text = small_font.render(level, True, color)  #English levels rõ
            text_rect = text.get_rect(center=(gv.SCREENWIDTH // 2, 250 + i * 80))  #y = 220 + i*60 (khoảng cách 60px như mainMenu)

            #Vẽ khung button bo tròn + hover scale
            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                gv.SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )
            pygame.draw.rect(gv.SCREEN, (50, 50, 50), button_rect, border_radius=10)  # Nền xám bo tròn
            pygame.draw.rect(gv.SCREEN, color, button_rect, 2, border_radius=10)  # Border color

            #Blit text (scale nếu hover)
            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                gv.SCREEN.blit(scaled_text, scaled_rect)
            else:
                gv.SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)  # Lưu hitbox cho click/hover

        #Hướng dẫn English + gesture
        instr_lines = ['Arrow keys / Gesture', 'Enter / Click']  #Split tại '|' để xuống dòng
        line_height = small_font.get_height() * 1.2  #Chiều cao dòng + spacing 20% (thoáng)
        y_base = 420  #Bắt đầu y=420 (dịch xuống từ 430, cách button ~80px)

        for i, line in enumerate(instr_lines):
            instr_text = small_font.render(line, True, (255, 255, 255))  # Render từng dòng
            instr_x = gv.SCREENWIDTH // 2 - instr_text.get_width() // 2  # Căn giữa x
            instr_y = y_base + i * line_height  # y tăng dần cho mỗi dòng
            gv.SCREEN.blit(instr_text, (instr_x, instr_y + 200))

        pygame.display.update()
        clock.tick(FPS)
