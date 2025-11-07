from global_variables import *
import cv2
import sys
import random
import pygame
import numpy as np
import json  # Đọc/ghi dữ liệu điểm cao vào file JSON
import os
from pygame.locals import *
import global_variables as gv


# =======================================================
# 1. HÀM ĐỌC DANH SÁCH ĐIỂM CAO TỪ FILE JSON
# =======================================================
def load_high_scores():
    try:
        with open(gv.HIGH_SCORES_FILE, 'r') as f:
            gv.high_scores = json.load(f)  # Đọc danh sách điểm cao
            # Sắp xếp giảm dần theo điểm, chỉ giữ 5 người cao nhất
            gv.high_scores = sorted(gv.high_scores, key=lambda x: x['score'], reverse=True)[:5]
    except FileNotFoundError:
        gv.high_scores = []  # Nếu chưa có file → khởi tạo rỗng


# =======================================================
# 2. HÀM LƯU ĐIỂM MỚI VÀO FILE JSON
# =======================================================
def save_high_score(name, score):
    gv.high_scores.append({'name': name, 'score': score})
    # Sắp xếp lại, chỉ giữ top 5
    gv.high_scores = sorted(gv.high_scores, key=lambda x: x['score'], reverse=True)[:5]
    # Ghi ra file JSON
    with open(gv.HIGH_SCORES_FILE, 'w') as f:
        json.dump(gv.high_scores, f)


# =======================================================
# 3. MÀN HÌNH NHẬP TÊN KHI KẾT THÚC TRÒ CHƠI
# =======================================================
def enterNameScreen(score):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * gv.SCALE_FACTOR), bold=True)
    small_font = pygame.font.SysFont('dejavusans', int(20 * gv.SCALE_FACTOR))

    player_name = ''        # Chuỗi nhập tên người chơi
    frame_count = 0         # Đếm frame để làm hiệu ứng nhấp nháy con trỏ
    selected = 0            # 0 = Save Name, 1 = Cancel
    options = ['Save Name', 'Cancel']
    button_rects = []       # Danh sách vùng bấm chuột
    hover_index = -1        # Vị trí nút đang hover
    angles = [None]         # Dùng gesture nếu có camera

    while True:
        frame_count += 1
        mouse_pos = pygame.mouse.get_pos()

        # ============ Nhận diện bàn tay (gesture) ============
        if gv.cap:
            ret, img = gv.cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = gv.hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])
                gv.hand.draw2d(img, param)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)

        # ============ Xử lý sự kiện bàn phím / chuột ============
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gv.MENU_STATE = 'main'  # Trở lại menu chính
                return

            elif event.type == KEYDOWN:
                # Nhấn Enter để lưu điểm
                if event.key == K_RETURN:
                    if player_name and selected == 0:
                        save_high_score(player_name, score)
                        gv.MENU_STATE = 'highscore'
                        return
                # Xoá ký tự cuối (Backspace)
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                # Gõ chữ cái (tự động chuyển thành in hoa)
                elif len(player_name) < gv.MAX_NAME_LENGTH and event.unicode.isalpha():
                    player_name += event.unicode.upper()

                # Di chuyển giữa các nút Save / Cancel
                elif event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected = 0
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected = 1

            elif event.type == MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                else:
                    hover_index = -1

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0 and player_name:
                            save_high_score(player_name, score)
                            gv.MENU_STATE = 'highscore'
                            return
                        elif i == 1:
                            gv.MENU_STATE = 'main'
                            return

        # ============ VẼ GIAO DIỆN NHẬP TÊN ============
        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))
        title = font.render('Game Over! Enter Name:', True, (255, 0, 0))
        gv.SCREEN.blit(title, (gv.SCREENWIDTH // 2 - title.get_width() // 2, 100))

        # Hiệu ứng nhấp nháy con trỏ nhập tên
        cursor = '|' if frame_count % 60 < 30 else ''
        name_text = font.render(player_name + cursor, True, (255, 255, 255))
        gv.SCREEN.blit(name_text, (gv.SCREENWIDTH // 2 - name_text.get_width() // 2, 200))

        # Hiển thị điểm
        score_text = small_font.render(f'Your Score: {score}', True, (255, 255, 0))
        gv.SCREEN.blit(score_text, (gv.SCREENWIDTH // 2 - score_text.get_width() // 2, 280))

        # ============ Vẽ 2 nút: Save Name / Cancel ============
        button_rects = []
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 0, 0) if is_selected else (255, 255, 0) if is_hover else (255, 255, 255)
            text = small_font.render(option, True, color)
            text_rect = text.get_rect(center=(gv.SCREENWIDTH // 2, 350 + i * 60))

            # Bo góc và scale khi hover
            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                gv.SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )
            pygame.draw.rect(gv.SCREEN, (50, 50, 50), button_rect, border_radius=10)
            pygame.draw.rect(gv.SCREEN, color, button_rect, 2, border_radius=10)

            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                gv.SCREEN.blit(scaled_text, scaled_rect)
            else:
                gv.SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)

        # Hướng dẫn
        instr = small_font.render('Type name + Enter/Click (ESC to exit)', True, (255, 255, 255))
        gv.SCREEN.blit(instr, (gv.SCREENWIDTH // 2 - instr.get_width() // 2, 650))

        pygame.display.update()
        clock.tick(FPS)


# =======================================================
# 4. MÀN HÌNH HIỂN THỊ DANH SÁCH ĐIỂM CAO
# =======================================================
def highScoreScreen():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * gv.SCALE_FACTOR), bold=True)
    small_font = pygame.font.SysFont('dejavusans', int(20 * gv.SCALE_FACTOR))

    gv.selected_index = 0
    button_rects = []
    hover_index = -1

    while True:
        mouse_pos = pygame.mouse.get_pos()
        angles = [None]

        # ============ Gesture (nếu có camera) ============
        if gv.cap:
            ret, img = gv.cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = gv.hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])
                gv.hand.draw2d(img, param)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)

        # ============ Xử lý sự kiện ============
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gv.MENU_STATE = 'main'
                return
            elif event.type == KEYDOWN:
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    gv.selected_index = max(0, gv.selected_index - 1)
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    gv.selected_index = min(len(gv.high_scores) - 1, gv.selected_index + 1)
                elif event.key == K_RETURN and gv.selected_index < len(gv.high_scores):
                    gv.MENU_STATE = 'delete_confirm'
                    confirmDelete(gv.selected_index)

            elif event.type == MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                else:
                    hover_index = -1

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos) and i < len(gv.high_scores):
                        gv.selected_index = i
                        gv.MENU_STATE = 'delete_confirm'
                        confirmDelete(i)

        # ============ Vẽ danh sách điểm cao ============
        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))
        title = font.render('High Scores', True, (255, 255, 255))
        gv.SCREEN.blit(title, (gv.SCREENWIDTH // 2 - title.get_width() // 2, 100))

        if gv.high_scores:
            button_rects = []
            for i, entry in enumerate(gv.high_scores):
                is_selected = (i == gv.selected_index)
                is_hover = (i == hover_index)
                color = (255, 215, 0) if is_hover else (255, 255, 0) if is_selected else (255, 255, 255)
                text = small_font.render(f'{i+1}. {entry["name"]} - {entry["score"]}', True, color)
                text_rect = text.get_rect(center=(gv.SCREENWIDTH // 2, 250 + i * 60))

                scale = 1.1 if is_hover else 1.0
                button_width = int((text_rect.width + 40) * scale)
                button_height = int((text_rect.height + 20) * scale)
                button_rect = pygame.Rect(
                    gv.SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                    button_width, button_height
                )
                pygame.draw.rect(gv.SCREEN, (50, 50, 50), button_rect, border_radius=10)
                pygame.draw.rect(gv.SCREEN, color, button_rect, 2, border_radius=10)

                if is_hover:
                    scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                    scaled_rect = scaled_text.get_rect(center=text_rect.center)
                    gv.SCREEN.blit(scaled_text, scaled_rect)
                else:
                    gv.SCREEN.blit(text, text_rect)
                button_rects.append(button_rect)
        else:
            no_score = small_font.render('No scores yet!', True, (255, 0, 0))
            gv.SCREEN.blit(no_score, (gv.SCREENWIDTH // 2 - no_score.get_width() // 2, 220))

        instr_lines = ['Select + Enter to delete', 'ESC to back']
        for i, line in enumerate(instr_lines):
            instr_text = small_font.render(line, True, (255, 255, 255))
            gv.SCREEN.blit(instr_text, (gv.SCREENWIDTH // 2 - instr_text.get_width() // 2, 650 + i * 30))

        pygame.display.update()
        clock.tick(FPS)


# =======================================================
# 5. HỘP XÁC NHẬN XOÁ (1 ENTRY HOẶC TOÀN BỘ)
# =======================================================
def confirmDelete(index_to_delete):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(25 * gv.SCALE_FACTOR), bold=True)

    selected = 0
    options = ['Delete This Entry', 'Delete All', 'Cancel']
    button_rects = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        hover_index = -1

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == K_RETURN:
                    handle_button_click(selected, index_to_delete)
                    return
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                    else:
                        hover_index = -1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        handle_button_click(i, index_to_delete)
                        return

        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))
        confirm_title = font.render('Delete this entry?', True, (255, 0, 0))
        gv.SCREEN.blit(confirm_title, (gv.SCREENWIDTH // 2 - confirm_title.get_width() // 2, 100))

        # Hiển thị entry đang chọn xoá
        try:
            entry_text = font.render(f'{gv.high_scores[index_to_delete]["name"]} - {gv.high_scores[index_to_delete]["score"]}', True, (255, 255, 255))
        except IndexError:
            entry_text = font.render('Entry does not exist!', True, (255, 0, 0))
        gv.SCREEN.blit(entry_text, (gv.SCREENWIDTH // 2 - entry_text.get_width() // 2, 200))

        # Vẽ 3 nút lựa chọn
        button_rects = []
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 0, 0) if is_selected else (255, 255, 0) if is_hover else (255, 255, 255)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(gv.SCREENWIDTH // 2, 300 + i * 80))

            scale = 1.05 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(gv.SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10, button_width, button_height)

            pygame.draw.rect(gv.SCREEN, (50, 50, 50), button_rect, border_radius=10)
            pygame.draw.rect(gv.SCREEN, color, button_rect, 3, border_radius=10)

            gv.SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)

        instr = font.render('Arrow keys / Click to select', True, (255, 255, 255))
        gv.SCREEN.blit(instr, (gv.SCREENWIDTH // 2 - instr.get_width() // 2, 650))

        pygame.display.update()
        clock.tick(gv.FPS)


# =======================================================
# 6. HÀM PHỤ XỬ LÝ XOÁ ENTRY HOẶC TOÀN BỘ
# =======================================================
def handle_button_click(button_index, index_to_delete):
    if button_index == 0:  # Xoá 1 entry cụ thể
        try:
            entry_name = gv.high_scores[index_to_delete]['name']
            del gv.high_scores[index_to_delete]
            with open(gv.HIGH_SCORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(gv.high_scores, f, indent=4, ensure_ascii=False)
            print(f"Đã xoá {entry_name} thành công!")
            if not gv.IS_MUTED:
                gv.GAME_SOUNDS['swoosh'].play()
        except IndexError:
            print("Lỗi: Entry không tồn tại!")

    elif button_index == 1:  # Xoá toàn bộ
        gv.high_scores = []
        with open(gv.HIGH_SCORES_FILE, 'w') as f:
            json.dump(gv.high_scores, f)
        print("Đã xoá toàn bộ bảng điểm!")
        if not gv.IS_MUTED:
            gv.GAME_SOUNDS['swoosh'].play()
    # button_index == 2 → Cancel, không làm gì
