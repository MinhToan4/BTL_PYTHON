from global_variables import *
import cv2
import sys  # Dùng sys.exit() để thoát chương trình
import random  # Tạo số ngẫu nhiên
import pygame
import numpy as np
import json   # Dùng để lưu điểm cao vào file JSON
import os
from random_pipe import getRandomPipe
from pygame.locals import *  # Import hằng số cơ bản của pygame (KEYDOWN, QUIT,...)
from highscores_process import enterNameScreen
import global_variables as gv


def mainGame():
    # ====== 1. KHỞI TẠO BIẾN BAN ĐẦU ======
    score = 0
    playerx = int(gv.SCREENWIDTH / 5)   # Vị trí ban đầu của chim theo trục X
    playery = int(gv.SCREENWIDTH / 2)   # Vị trí ban đầu của chim theo trục Y
    basex = 0                           # Vị trí nền đất (base)

    pipeVelX = gv.DIFFICULTY_LEVELS[gv.current_difficulty]['pipe_vel_x']

    # Tạo 2 cặp ống đầu tiên
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Danh sách ống trên
    upperPipes = [
        {'x': gv.SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': gv.SCREENWIDTH + 200 + (gv.SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # Danh sách ống dưới
    lowerPipes = [
        {'x': gv.SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': gv.SCREENWIDTH + 200 + (gv.SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4  # Vận tốc di chuyển ống sang trái

    # ====== 2. THIẾT LẬP VẬT LÝ CHO CHIM ======
    playerVelY = -9         # Tốc độ rơi ban đầu
    playerMaxVelY = 10      # Tốc độ rơi tối đa
    playerMinVelY = -8      # Tốc độ bay lên tối đa
    playerAccY = 1          # Gia tốc rơi xuống

    playerFlapAccv = -8     # Vận tốc khi vỗ cánh
    playerFlapped = False   # True khi chim vỗ cánh
    GESTURE_THRESHOLD = 55  # Ngưỡng góc tay (độ) để nhận biết vỗ cánh bằng gesture
    prev_angle_above = [False, False]  # Trạng thái “tay đang giơ cao” cho 2 tay

    # ====== 3. VÒNG LẶP CHÍNH CỦA GAME ======
    while True:
        angles = [None, None]  # Lưu góc tay cho 2 tay

        # --- Xử lý camera / MediaPipe ---
        if gv.cap is not None:
            ret, img = gv.cap.read()
            if ret:
                img = cv2.flip(img, 1)  # Lật ảnh để giống gương
                try:
                    param = gv.hand.forward(img)  # Phân tích khung tay
                except Exception as err:
                    print("[ERROR] Hand forward error:", err)
                    param = []

                # Lấy góc trung bình cho mỗi tay
                for i in range(min(2, len(param))):
                    if param[i]['class'] is not None:
                        angles[i] = float(np.mean(param[i]['angle']))

                # Vẽ khung tay và hiển thị góc tay
                img = gv.hand.draw2d(img.copy(), param)
                cv2.putText(img, f"Angle L: {angles[0] if angles[0] is not None else -1:.1f}", (10,30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.putText(img, f"Angle R: {angles[1] if angles[1] is not None else -1:.1f}", (10,70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)

        # Nếu không có camera thì tạo giá trị giả lập
        if (gv.cap is None or gv.using_mock) and 'param' not in locals():
            try:
                param = gv.hand.forward(np.zeros((480,640,3), dtype=np.uint8))
                angles[0] = float(np.mean(param[0]['angle']))
            except Exception:
                angles[0] = None

        # ====== 4. XỬ LÝ SỰ KIỆN BÀN PHÍM ======
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    if not gv.IS_MUTED: gv.GAME_SOUNDS['wing'].play()

        # ====== 5. XỬ LÝ GESTURE VỖ CÁNH (tay) ======
        if gv.cap is not None and not gv.using_mock:
            for i in range(2):
                if angles[i] is not None:
                    angle_above = angles[i] > GESTURE_THRESHOLD
                    # Khi tay vừa vượt ngưỡng từ dưới lên → vỗ cánh
                    if angle_above and not prev_angle_above[i] and playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        if not gv.IS_MUTED: gv.GAME_SOUNDS['wing'].play()
                    prev_angle_above[i] = angle_above

        # ====== 6. KIỂM TRA VA CHẠM ======
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest and not gv.GOD_MODE:
            if not gv.IS_MUTED:
                gv.GAME_SOUNDS['hit'].play()
                gv.GAME_SOUNDS['die'].play()
            enterNameScreen(score)
            return score  # Thoát game và trả điểm

        # ====== 7. CỘNG ĐIỂM ======
        playerMidPos = playerx + gv.GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + gv.GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                if not gv.IS_MUTED: gv.GAME_SOUNDS['point'].play()

        # ====== 8. CẬP NHẬT VẬT LÝ ======
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY  # Rơi xuống (tăng tốc độ Y)
        if playerFlapped:
            playerFlapped = False

        playerHeight = gv.GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, gv.GROUNDY - playery - playerHeight)
        playery = max(0, min(playery, gv.GROUNDY - playerHeight))  # Giữ trong màn hình

        # ====== 9. DI CHUYỂN ỐNG ======
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Khi ống gần hết bên trái → thêm ống mới
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # Khi ống cũ ra khỏi màn hình → xóa
        if upperPipes[0]['x'] < -gv.GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # ====== 10. VẼ KHUNG HÌNH ======
        gv.SCREEN.blit(gv.GAME_SPRITES['background'], (0, 0))

        # Vẽ các ống
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            gv.SCREEN.blit(gv.GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            gv.SCREEN.blit(gv.GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        # Vẽ mặt đất
        gv.SCREEN.blit(gv.GAME_SPRITES['base'], (basex, gv.GROUNDY))
        gv.SCREEN.blit(gv.GAME_SPRITES['base'], (basex + gv.GAME_SPRITES['base'].get_width(), gv.GROUNDY))

        # Vẽ chim
        gv.SCREEN.blit(gv.GAME_SPRITES['player'], (playerx, playery))

        # Hiển thị điểm
        myDigits = [int(x) for x in list(str(score))]
        width = sum(gv.GAME_SPRITES['numbers'][d].get_width() for d in myDigits)
        Xoffset = (gv.SCREENWIDTH - width) / 2

        for digit in myDigits:
            gv.SCREEN.blit(gv.GAME_SPRITES['numbers'][digit], (Xoffset, gv.SCREENHEIGHT * 0.12))
            Xoffset += gv.GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        gv.FPSCLOCK.tick(gv.FPS)  # Giới hạn FPS


# ====== HÀM PHỤ: KIỂM TRA VA CHẠM ======
def isCollide(playerx, playery, upperPipes, lowerPipes):
    # Va vào đất hoặc trần
    if playery > gv.GROUNDY - 25 or playery < 0:
        if not gv.GOD_MODE and not gv.IS_MUTED:
            gv.GAME_SOUNDS['hit'].play()
        return not gv.GOD_MODE

    # Va vào ống trên
    for pipe in upperPipes:
        pipeHeight = gv.GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < gv.GAME_SPRITES['pipe'][0].get_width()):
            if not gv.GOD_MODE and not gv.IS_MUTED:
                gv.GAME_SOUNDS['hit'].play()
            return not gv.GOD_MODE

    # Va vào ống dưới
    for pipe in lowerPipes:
        if (playery + gv.GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < gv.GAME_SPRITES['pipe'][0].get_width():
            if not gv.GOD_MODE and not gv.IS_MUTED:
                gv.GAME_SOUNDS['hit'].play()
            return not gv.GOD_MODE

    return False
