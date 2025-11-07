from global_variables import *
import cv2
import sys  # Dùng sys.exit() để thoát hoàn toàn chương trình
import random  # Dùng cho hiệu ứng ngẫu nhiên (nếu cần)
import pygame
import numpy as np
import json
import os
from pygame.locals import *  # Các hằng cơ bản của Pygame như QUIT, KEYDOWN, MOUSEBUTTONDOWN,...
import global_variables as gv


def mainMenu():
    # ====== 1. THIẾT LẬP CƠ BẢN CHO MENU ======
    clock = pygame.time.Clock()  # Dùng để giới hạn FPS của menu
    font = pygame.font.SysFont('dejavusans', int(40 * gv.SCALE_FACTOR), bold=True)  # Font tiêu đề lớn
    small_font = pygame.font.SysFont('dejavusans', int(30 * gv.SCALE_FACTOR))       # Font cho nút

    selected = 0  # Chỉ số mục đang chọn (Start = 0, Score Board = 1)
    options = ['Start', 'Score Board']  # Danh sách lựa chọn trong menu
    button_rects = []  # Lưu vị trí các nút để xử lý click chuột
    hover_index = -1   # Chỉ số nút đang được hover chuột
    frame_count = 0    # Đếm frame để làm hiệu ứng animation

    # ====== 2. HIỆU ỨNG FADE-IN CHO TIÊU ĐỀ ======
    if gv.MENU_FADE_ALPHA < 255:
        gv.MENU_FADE_ALPHA += 5  # Tăng độ trong suốt dần dần (từ mờ → rõ)
        if gv.MENU_FADE_ALPHA > 255:
            gv.MENU_FADE_ALPHA = 255

    # ====== 3. VÒNG LẶP MENU CHÍNH ======
    while True:
        frame_count += 1
        mouse_pos = pygame.mouse.get_pos()
        angles = [None]  # Mảng góc tay (MediaPipe) — chỉ dùng 1 tay cho menu

        # --- 3.1. XỬ LÝ GESTURE TAY (MediaPipe) ---
        if gv.cap:  # Nếu có camera
            ret, img = gv.cap.read()
            if ret:
                img = cv2.flip(img, 1)  # Lật ảnh theo chiều ngang cho giống gương
                param = gv.hand.forward(img)  # Phân tích bàn tay
                if param:
                    angles[0] = np.mean(param[0]['angle'])  # Tính góc trung bình các khớp tay
                gv.hand.draw2d(img, param)  # Vẽ bàn tay lên ảnh
                cv2.imshow('Hand', img)
                cv2.waitKey(1)

        # --- 3.2. XỬ LÝ SỰ KIỆN TỪ BÀN PHÍM / CHUỘT ---
        for event in pygame.event.get():
            # Thoát game nếu nhấn ESC hoặc đóng cửa sổ
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Điều hướng menu bằng bàn phím hoặc gesture tay
            elif event.type == KEYDOWN:
                # Di chuyển lên
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected = (selected - 1) % len(options)
                # Di chuyển xuống
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected = (selected + 1) % len(options)
                # Xác nhận chọn (Enter / Space)
                elif event.key in (K_RETURN, K_SPACE):
                    if selected == 0:
                        gv.MENU_STATE = 'difficulty'  # Sang chọn độ khó
                        return
                    elif selected == 1:
                        gv.MENU_STATE = 'highscore'   # Sang bảng điểm
                        return

            # Di chuột qua nút
            elif event.type == MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                    else:
                        hover_index = -1

            # Click chuột trái vào nút
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:
                            gv.MENU_STATE = 'difficulty'
                            return
                        elif i == 1:
                            gv.MENU_STATE = 'highscore'
                            return

        # ====== 4. VẼ NỀN (BACKGROUND + BASE CUỘN) ======
        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))
        basex = frame_count % gv.SCREENWIDTH  # Làm nền đất cuộn chậm để sinh động
        gv.SCREEN.blit(gv.GAME_SPRITES['base'], (basex - gv.SCREENWIDTH, gv.GROUNDY))
        gv.SCREEN.blit(gv.GAME_SPRITES['base'], (basex, gv.GROUNDY))

        # ====== 5. TIÊU ĐỀ GAME (FADE-IN) ======
        title_surface = font.render('Flappy Bird', True, (255, 255, 255))
        title_surface.set_alpha(gv.MENU_FADE_ALPHA)
        title_rect = title_surface.get_rect(center=(gv.SCREENWIDTH // 2, 100))
        gv.SCREEN.blit(title_surface, title_rect)

        # ====== 6. HIỆU ỨNG CHIM NHÚN NHẢY Ở GÓC TRÁI ======
        gv.BIRD_ANIM_ANGLE += 1  # Quay 1 độ mỗi frame
        if gv.BIRD_FLAP_FRAME % 60 == 0:  # Vỗ cánh mỗi 60 frame (khoảng 2 giây ở 30FPS)
            gv.BIRD_FLAP_FRAME = 0
        gv.BIRD_FLAP_FRAME += 1
        idle_bird = pygame.transform.rotate(
            gv.GAME_SPRITES['player'],
            gv.BIRD_ANIM_ANGLE % 360
        )
        gv.SCREEN.blit(idle_bird, (50, 150))

        # ====== 7. VẼ NÚT MENU ======
        button_rects = []
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)

            # Màu sắc khác nhau cho các trạng thái
            color = (
                (255, 215, 0) if is_hover else
                (255, 255, 0) if is_selected else
                (255, 255, 255)
            )

            # Tạo chữ
            text = small_font.render(option, True, color)
            text_rect = text.get_rect(center=(gv.SCREENWIDTH // 2, 250 + i * 80))

            # Phóng to nhẹ khi hover
            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                gv.SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )

            # Vẽ bóng đổ cho nút
            shadow_rect = button_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(gv.SCREEN, (0, 0, 0, 100), shadow_rect, border_radius=10)

            # Vẽ nút chính
            pygame.draw.rect(gv.SCREEN, (50, 50, 50), button_rect, border_radius=10)
            pygame.draw.rect(gv.SCREEN, color, button_rect, 3, border_radius=10)

            # Vẽ chữ (phóng to nếu hover)
            if is_hover:
                scaled_text = pygame.transform.scale(
                    text,
                    (int(text.get_width() * scale), int(text.get_height() * scale))
                )
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                gv.SCREEN.blit(scaled_text, scaled_rect)
            else:
                gv.SCREEN.blit(text, text_rect)

            button_rects.append(button_rect)

        # ====== 8. HIỂN THỊ HƯỚNG DẪN ĐIỀU KHIỂN ======
        instr = small_font.render('↑ ↓ | Enter / Click', True, (255, 255, 255))
        gv.SCREEN.blit(instr, (gv.SCREENWIDTH // 2 - instr.get_width() // 2, 650))

        # ====== 9. CẬP NHẬT MÀN HÌNH ======
        pygame.display.update()
        clock.tick(FPS)  # Giới hạn tốc độ khung hình
