import cv2
import sys
import random
import pygame
import numpy as np
import json 
import os
from highscores_process import load_high_scores, save_high_score, enterNameScreen, highScoreScreen, confirmDelete, handle_button_click
from main_menu import mainMenu
from game_process import  mainGame, isCollide
from difficulty_menu import difficultyMenu
from scale_images import scale_image
from random_pipe import getRandomPipe
from global_variables import *
from pygame.locals import * # Basic pygame imports
import global_variables as gv

# Kiểm tra file utils_mediapipe có hoạt động hay không nếu không thì dùng file utils_mediapipe_mock để tạo các toạ độ ảo
gv.using_mock = False
try:
    from utils_mediapipe import MediaPipeHand
except Exception as e:
    from utils_mediapipe_mock import MediaPipeHand
    gv.using_mock = True
    print("[INFO] Using mock MediaPipe hand tracking (real mediapipe not available):", e)

# Kiểm tra camera có hoạt động hay không
for i in range(5):
    test_cap = cv2.VideoCapture(i)
    if test_cap.isOpened():
        ret, frame = test_cap.read()
        if ret:
            gv.cap = test_cap
            print(f"Found camera at index {i}")
            break
        else:
            test_cap.release()
    else:
        test_cap.release()

if gv.cap is None:
    print("No camera found - running in keyboard-only mode")

# Tạo mediaPipeHand để nhận diện bàn tay
gv.hand = MediaPipeHand(static_image_mode=False, max_num_hands=2)
 
if __name__ == "__main__":
    #Khởi tạo pygame
    pygame.init()
    gv.FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('VTV_VietToanVy_BTL_Python')

    load_high_scores()

    # Tải hình ảnh đồ hoạ cho các đối tượng
    gv.GAME_SPRITES['numbers'] = (
        pygame.image.load(r'gallery\sprites\0.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\1.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\2.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\3.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\4.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\5.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\6.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\7.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\8.png').convert_alpha(),
        pygame.image.load(r'gallery\sprites\9.png').convert_alpha(),
    )

    gv.GAME_SPRITES['message'] =pygame.image.load(r'gallery\sprites\message.png').convert_alpha()
    
    gv.GAME_SPRITES['base'] = scale_image(pygame.image.load(r'gallery\sprites\base.png').convert_alpha(), gv.SCALE_FACTOR)
    gv.GAME_SPRITES['pipe'] = (
        scale_image(pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180), gv.SCALE_FACTOR),
        scale_image(pygame.image.load(PIPE).convert_alpha(), gv.SCALE_FACTOR)
    )
    # Tải âm thanh cho trò chơi
    gv.GAME_SOUNDS['die'] = pygame.mixer.Sound(r'gallery\audio\die.wav')
    gv.GAME_SOUNDS['hit'] = pygame.mixer.Sound(r'gallery\audio\hit.wav')
    gv.GAME_SOUNDS['point'] = pygame.mixer.Sound(r'gallery\audio\point.wav')
    gv.GAME_SOUNDS['swoosh'] = pygame.mixer.Sound(r'gallery\audio\swoosh.wav')
    gv.GAME_SOUNDS['wing'] = pygame.mixer.Sound(r'gallery\audio\wing.wav')

    gv.GAME_SPRITES['background'] = scale_image(pygame.image.load(gv.BACKGROUND).convert(), gv.SCALE_FACTOR)
    gv.GAME_SPRITES['player'] = scale_image(pygame.image.load(gv.PLAYER).convert_alpha(), gv.SCALE_FACTOR)

    # Vòng lặp vô hạn để chuyển tiếp giữa các màn hình tương ứng với các trạng thái khác nhau
    while True:
        if gv.MENU_STATE == 'main':
            mainMenu()
        elif gv.MENU_STATE == 'difficulty':
            difficultyMenu()
        elif gv.MENU_STATE == 'highscore':
            highScoreScreen()
        elif gv.MENU_STATE == 'enter_name':
            gv.MENU_STATE = 'highscore'
        elif gv.MENU_STATE == 'delete_confirm':
            confirmDelete(selected_index)
            gv.MENU_STATE = 'highscore'
        elif gv.MENU_STATE == 'playing':
            curent_score = mainGame()
            gv.MENU_STATE = 'enter_name'