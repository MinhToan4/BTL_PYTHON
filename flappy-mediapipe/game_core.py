import cv2
import sys # We will use sys.exit to exit the program
import random # For generating random numbers
import pygame
import numpy as np
import json  # Để lưu high scores JSON
import os

from pygame.locals import * # Basic pygame imports

# Try to import real MediaPipe wrapper; fallback to mock
using_mock = False
try:
    from utils_mediapipe import MediaPipeHand
except Exception as e:
    from utils_mediapipe_mock import MediaPipeHand
    using_mock = True
    print("[INFO] Using mock MediaPipe hand tracking (real mediapipe not available):", e)

# Global Variables for the game
SCALE_FACTOR = 1.5
FPS = 32
SCREENWIDTH = int(289 *SCALE_FACTOR)
SCREENHEIGHT = int(511 * SCALE_FACTOR)
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
IS_MUTED = False  # Mute all sounds if True
GOD_MODE = False   # If True, bird never dies
PLAYER = r'gallery\sprites\bird.png'
BACKGROUND = r'gallery\sprites\background.png'
PIPE = r'gallery\sprites\pipe.png'
MENU_STATE = 'main'  # 'main', 'difficulty', 'highscore', 'playing'
DIFFICULTY_LEVELS = {
    'Easy': {'pipe_vel_x': -3, 'gap_offset': SCREENHEIGHT / 3 * 1.5},  # Chậm, gap rộng
    'Medium': {'pipe_vel_x': -4, 'gap_offset': SCREENHEIGHT / 3},      # Mặc định
    'Hard': {'pipe_vel_x': -6, 'gap_offset': SCREENHEIGHT / 3 * 0.8}   # Nhanh, gap hẹp
}
HIGH_SCORES_FILE = 'highscores.json'
high_scores = []
MAX_NAME_LENGTH = 10  # Giới hạn tên nhập
# current_difficulty = os.environ.get('DIFFICULTY', 'Medium')
current_difficulty = 'Medium'  # Mặc định
current_score = 0
selected_index = 0

MENU_FADE_ALPHA = 255  # Alpha cho title fade-in (bắt đầu mờ)
BIRD_ANIM_ANGLE = 0  # Góc xoay chim idle
BIRD_FLAP_FRAME = 0

def load_high_scores():
    global high_scores
    try:
        with open(HIGH_SCORES_FILE, 'r') as f:
            high_scores = json.load(f)
            high_scores = sorted(high_scores, key=lambda x: x['score'], reverse=True)[:5]  # Sort theo score, top 5
    except FileNotFoundError:
        high_scores = []

def save_high_score(name, score):
    global high_scores
    high_scores.append({'name': name, 'score': score})
    high_scores = sorted(high_scores, key=lambda x: x['score'], reverse=True)[:5]
    with open(HIGH_SCORES_FILE, 'w') as f:
        json.dump(high_scores, f)
# Load Classes for Hand Tracking
# Try to find an available camera, starting from index 0
cap = None
for i in range(5):  # Try cameras 0-4
    test_cap = cv2.VideoCapture(i)
    if test_cap.isOpened():
        ret, frame = test_cap.read()
        if ret:
            cap = test_cap
            print(f"Found camera at index {i}")
            break
        else:
            test_cap.release()
    else:
        test_cap.release()

if cap is None:
    print("No camera found - running in keyboard-only mode")

hand = MediaPipeHand(static_image_mode=False, max_num_hands=2)

def mainMenu():
    global MENU_STATE, MENU_FADE_ALPHA, BIRD_ANIM_ANGLE, BIRD_FLAP_FRAME  # Global cho animation
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(40 * SCALE_FACTOR), bold=True)  # UTF-8 + scale
    small_font = pygame.font.SysFont('dejavusans', int(30 * SCALE_FACTOR))

    selected = 0
    options = ['Start', 'Score Board']  # Tiếng Việt UTF-8
    button_rects = []
    hover_index = -1
    frame_count = 0  # Timer cho animation (tăng mỗi frame)

    # Fade-in title khi vào menu (một lần)
    if MENU_FADE_ALPHA < 255:
        MENU_FADE_ALPHA += 5  # Tăng alpha dần (mờ → rõ)
        if MENU_FADE_ALPHA > 255:
            MENU_FADE_ALPHA = 255

    while True:
        frame_count += 1  # Cập nhật timer
        mouse_pos = pygame.mouse.get_pos()
        angles = [None]  # Gesture đơn giản cho menu

        # Gesture (tùy chọn, nếu cap)
        if cap:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])
                hand.draw2d(img, param)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected = (selected - 1) % len(options)
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected = (selected + 1) % len(options)
                elif event.key in (K_RETURN, K_SPACE):
                    if selected == 0:
                        MENU_STATE = 'difficulty'
                        return
                    elif selected == 1:
                        MENU_STATE = 'highscore'
                        return
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
                        if i == 0:
                            MENU_STATE = 'difficulty'
                            return
                        elif i == 1:
                            MENU_STATE = 'highscore'
                            return

        # Vẽ background (thêm subtle animation: ground scroll chậm)
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        basex = frame_count % SCREENWIDTH  # Di chuyển nền nhẹ (parallax)
        SCREEN.blit(GAME_SPRITES['base'], (basex - SCREENWIDTH, GROUNDY))  # Phần 1
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))  # Phần 2 loop

        # Title với fade-in (Surface alpha)
        title_surface = font.render('Flappy Bird', True, (255, 255, 255))
        title_surface.set_alpha(MENU_FADE_ALPHA)  # Fade alpha
        title_rect = title_surface.get_rect(center=(SCREENWIDTH // 2, 100))
        SCREEN.blit(title_surface, title_rect)

        # Bird idle animation ở góc (xoay nhẹ + flap)
        BIRD_ANIM_ANGLE += 1  # Xoay 1 độ mỗi frame
        if BIRD_FLAP_FRAME % 60 == 0:  # Flap mỗi 2s (60 frames ~2s tại 30FPS)
            BIRD_FLAP_FRAME = 0
        BIRD_FLAP_FRAME += 1
        idle_bird = pygame.transform.rotate(GAME_SPRITES['player'], BIRD_ANIM_ANGLE % 360)  # Xoay loop
        SCREEN.blit(idle_bird, (50, 150))  # Vị trí góc trái

        button_rects = []
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 215, 0) if is_hover else (255, 255, 0) if is_selected else (255, 255, 255)
            text = small_font.render(option, True, color)  # UTF-8 Việt rõ
            text_rect = text.get_rect(center=(SCREENWIDTH // 2, 250 + i * 80))

            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )
            
            # FIX: Thêm shadow (bóng đổ) cho button đẹp
            shadow_rect = button_rect.copy()
            shadow_rect.x += 3  # Offset shadow
            shadow_rect.y += 3
            pygame.draw.rect(SCREEN, (0, 0, 0, 100), shadow_rect, border_radius=10)  # Shadow đen mờ
            
            pygame.draw.rect(SCREEN, (50, 50, 50), button_rect, border_radius=10)  # Button nền
            pygame.draw.rect(SCREEN, color, button_rect, 3, border_radius=10)  # Border glow

            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                SCREEN.blit(scaled_text, scaled_rect)
            else:
                SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)

        instr = small_font.render('↑ ↓ | Enter / Click', True, (255, 255, 255))  # Hướng dẫn gesture
        SCREEN.blit(instr, (SCREENWIDTH // 2 - instr.get_width() // 2, 650))
        
        pygame.display.update()
        clock.tick(FPS)

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    pipeVelX = DIFFICULTY_LEVELS[current_difficulty]['pipe_vel_x']

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping
    GESTURE_THRESHOLD = 55  # angle (deg) above which we trigger a flap
    prev_angle_above = [False, False]  # cho 2 tay

    while True:
        angles = [None, None]  # Reset mỗi frame cho 2 tay
        if cap is not None:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                try:
                    param = hand.forward(img)
                except Exception as err:
                    print("[ERROR] Hand forward error:", err)
                    param = []
                # Vẽ và lấy góc cho từng tay
                for i in range(min(2, len(param))):
                    if param[i]['class'] is not None:
                        angles[i] = float(np.mean(param[i]['angle']))
                img = hand.draw2d(img.copy(), param)
                # Hiển thị góc của 2 tay
                cv2.putText(img, f"Angle L: {angles[0] if angles[0] is not None else -1:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.putText(img, f"Angle R: {angles[1] if angles[1] is not None else -1:.1f}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)
        # Nếu không có camera hoặc dùng mock, chỉ lấy tay đầu tiên
        if (cap is None or using_mock) and 'param' not in locals():
            try:
                param = hand.forward(np.zeros((480,640,3), dtype=np.uint8))
                angles[0] = float(np.mean(param[0]['angle']))
            except Exception:
                angles[0] = None

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    if not IS_MUTED: GAME_SOUNDS['wing'].play()

        # Gesture-based flap (cho 2 tay, chỉ cần 1 tay vượt ngưỡng là nhảy)
        if cap is not None and not using_mock:
            for i in range(2):
                if angles[i] is not None:
                    angle_above = angles[i] > GESTURE_THRESHOLD
                    if angle_above and not prev_angle_above[i] and playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        if not IS_MUTED: GAME_SOUNDS['wing'].play()
                    prev_angle_above[i] = angle_above

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest and not GOD_MODE:
            if not IS_MUTED: 
                GAME_SOUNDS['hit'].play()
                GAME_SOUNDS['die'].play()
            enterNameScreen(score)
            return score

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}")
                if not IS_MUTED: GAME_SOUNDS['point'].play()
        # Apply gravity / velocity AFTER scoring loop (once per frame)
        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        # Physics update only (remove direct angle->y mapping)
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        # Clamp playery inside screen
        if playery < 0: playery = 0
        if playery > GROUNDY - playerHeight: playery = GROUNDY - playerHeight

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        # basex += -pipeVelX  
        # if basex <= -GAME_SPRITES['base'].get_width():
        #     basex = 0
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['base'], (basex + GAME_SPRITES['base'].get_width(), GROUNDY))
        
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
        return not GOD_MODE

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
            return not GOD_MODE

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
            return not GOD_MODE

    return False


def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = int(DIFFICULTY_LEVELS[current_difficulty]['gap_offset'])
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe

def scale_image(image, factor):
    width = int(image.get_width() * factor)
    height = int(image.get_height() * factor)
    return pygame.transform.scale(image, (width, height))

def difficultyMenu():
    global MENU_STATE, current_difficulty
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * SCALE_FACTOR), bold=True)  # FIX: DejaVuSans + scale cho UTF-8 Anh/Việt nếu cần
    small_font = pygame.font.SysFont('dejavusans', int(25 * SCALE_FACTOR))  # FIX: Scale nhỏ hơn cho levels

    selected = 0
    levels = list(DIFFICULTY_LEVELS.keys())  # ['Easy', 'Medium', 'Hard'] – Giữ English
    button_rects = []  # FIX: List rect cho hover/click như mainMenu
    hover_index = -1  # FIX: Index hover mouse

    while True:
        mouse_pos = pygame.mouse.get_pos()  # FIX: Lấy vị trí chuột mỗi frame cho hover
        angles = [None]  # FIX: Gesture đơn giản cho menu (1 tay)

        # Gesture (tùy chọn, nếu cap) – FIX: Tích hợp như mainMenu
        if cap:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])  # Trung bình góc tay
                hand.draw2d(img, param)
                cv2.imshow('Hand', img)  # Window debug gesture
                cv2.waitKey(1)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                MENU_STATE = 'main'  # Quay về main menu
                return
            elif event.type == KEYDOWN:
                # FIX: UP/DOWN + gesture (thả tay >55 = UP, nắm <30 = DOWN)
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected = (selected - 1) % len(levels)
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected = (selected + 1) % len(levels)
                elif event.key == K_RETURN:
                    current_difficulty = levels[selected]
                    MENU_STATE = 'playing'
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
                        current_difficulty = levels[i]
                        MENU_STATE = 'playing'
                        return

        # Vẽ submenu – FIX: Giống mainMenu, background + title English
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        title = font.render('Select Difficulty', True, (255, 255, 255))  # FIX: English
        SCREEN.blit(title, (SCREENWIDTH // 2 - title.get_width() // 2, 100))

        button_rects = []  # FIX: Reset mỗi frame
        for i, level in enumerate(levels):  # FIX: Loop vẽ button cho mỗi level
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 215, 0) if is_hover else (255, 255, 0) if is_selected else (255, 255, 255)  # FIX: Color như mainMenu
            text = small_font.render(level, True, color)  # FIX: English levels rõ
            text_rect = text.get_rect(center=(SCREENWIDTH // 2, 250 + i * 80))  # FIX: y = 220 + i*60 (khoảng cách 60px như mainMenu)

            # FIX: Vẽ khung button bo tròn + hover scale
            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )
            pygame.draw.rect(SCREEN, (50, 50, 50), button_rect, border_radius=10)  # Nền xám bo tròn
            pygame.draw.rect(SCREEN, color, button_rect, 2, border_radius=10)  # Border color

            # FIX: Blit text (scale nếu hover)
            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                SCREEN.blit(scaled_text, scaled_rect)
            else:
                SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)  # Lưu hitbox cho click/hover

        # FIX: Hướng dẫn English + gesture
        instr_lines = ['Arrow keys / Gesture', 'Enter / Click']  # FIX: Split tại '|' để xuống dòng
        line_height = small_font.get_height() * 1.2  # FIX: Chiều cao dòng + spacing 20% (thoáng)
        y_base = 420  # FIX: Bắt đầu y=420 (dịch xuống từ 430, cách button ~80px)

        for i, line in enumerate(instr_lines):
            instr_text = small_font.render(line, True, (255, 255, 255))  # Render từng dòng
            instr_x = SCREENWIDTH // 2 - instr_text.get_width() // 2  # Căn giữa x
            instr_y = y_base + i * line_height  # FIX: y tăng dần cho mỗi dòng
            SCREEN.blit(instr_text, (instr_x, instr_y + 200))

        pygame.display.update()
        clock.tick(FPS)

def enterNameScreen(score):
    global MENU_STATE
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * SCALE_FACTOR), bold=True)  # DejaVuSans + scale cho UTF-8 English
    small_font = pygame.font.SysFont('dejavusans', int(20 * SCALE_FACTOR))  # Scale text

    player_name = ''  # Name input
    frame_count = 0  # Timer for blink cursor and gesture
    selected = 0  # Button index: 0=Save Name, 1=Cancel
    options = ['Save Name', 'Cancel']  # FIX: English buttons
    button_rects = []  # List rect for hover/click
    hover_index = -1  # Hover mouse index
    angles = [None]  # Gesture for menu (1 hand)

    while True:
        frame_count += 1  # Update timer each frame
        mouse_pos = pygame.mouse.get_pos()  # Get mouse pos for hover

        # Gesture (optional, if cap) – Integrated like difficultyMenu
        if cap:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])  # Average hand angle
                hand.draw2d(img, param)
                cv2.imshow('Hand', img)  # Gesture debug
                cv2.waitKey(1)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                MENU_STATE = 'main'
                return  # No save if ESC

            elif event.type == KEYDOWN:
                # Input name handling (keep original)
                if event.key == K_RETURN:  # Enter: Save (if button 0 selected)
                    if player_name and selected == 0:
                        save_high_score(player_name, score)
                        MENU_STATE = 'highscore'
                        return
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]  # Delete last char
                elif len(player_name) < MAX_NAME_LENGTH and event.unicode.isalpha():
                    player_name += event.unicode.upper()  # Add uppercase letter

                # UP/DOWN + gesture for buttons (open hand = Save, fist = Cancel)
                elif event.key == K_UP or (angles[0] > 55 if angles[0] else False):  # Open hand = select Save (0)
                    selected = 0
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):  # Fist = select Cancel (1)
                    selected = 1

            elif event.type == MOUSEMOTION:  # Hover effect like difficultyMenu
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                else:
                    hover_index = -1

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Click button
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0 and player_name:  # Save if name exists
                            save_high_score(player_name, score)
                            MENU_STATE = 'highscore'
                            return
                        elif i == 1:  # Cancel
                            MENU_STATE = 'main'
                            return

        # Draw name entry screen
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        title = font.render('Game Over! Enter Name:', True, (255, 0, 0))  # FIX: English title
        SCREEN.blit(title, (SCREENWIDTH // 2 - title.get_width() // 2, 100))

        # Name + blinking cursor (blinks every 1s)
        cursor = '|' if frame_count % 60 < 30 else ''  # Blink timer (30 frames on/off)
        name_text = font.render(player_name + cursor, True, (255, 255, 255))
        SCREEN.blit(name_text, (SCREENWIDTH // 2 - name_text.get_width() // 2, 200))

        score_text = small_font.render(f'Your Score: {score}', True, (255, 255, 0))  # FIX: English score
        SCREEN.blit(score_text, (SCREENWIDTH // 2 - score_text.get_width() // 2, 280))

        # Draw 2 buttons (like difficultyMenu, rounded + hover)
        button_rects = []  # Reset each frame
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 0, 0) if is_selected else (255, 255, 0) if is_hover else (255, 255, 255)
            text = small_font.render(option, True, color)  # Render button text
            text_rect = text.get_rect(center=(SCREENWIDTH // 2, 350 + i * 60))  # y=300 + i*60 (below score)

            # Button rect with hover scale
            scale = 1.1 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_rect = pygame.Rect(
                SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                button_width, button_height
            )
            pygame.draw.rect(SCREEN, (50, 50, 50), button_rect, border_radius=10)  # Gray background
            pygame.draw.rect(SCREEN, color, button_rect, 2, border_radius=10)  # Border

            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                SCREEN.blit(scaled_text, scaled_rect)
            else:
                SCREEN.blit(text, text_rect)
            button_rects.append(button_rect)

        # Instructions (keep concise)
        instr = small_font.render('Type name + Enter/Click (ESC to exit)', True, (255, 255, 255))  # FIX: English instr
        SCREEN.blit(instr, (SCREENWIDTH // 2 - instr.get_width() // 2, 650))

        pygame.display.update()
        clock.tick(FPS)

def highScoreScreen():
    global MENU_STATE, selected_index
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(30 * SCALE_FACTOR), bold=True)  # FIX: DejaVuSans + scale cho UTF-8 Anh/Việt nếu cần
    small_font = pygame.font.SysFont('dejavusans', int(20 * SCALE_FACTOR))  # FIX: Scale nhỏ hơn cho entries

    selected_index = 0
    button_rects = []  # FIX: List rect cho hover/click như difficultyMenu
    hover_index = -1  # FIX: Index hover mouse

    while True:
        mouse_pos = pygame.mouse.get_pos()  # FIX: Lấy vị trí chuột mỗi frame cho hover
        angles = [None]  # FIX: Gesture đơn giản cho menu (1 tay)

        # Gesture (tùy chọn, nếu cap) – FIX: Tích hợp như difficultyMenu
        if cap:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                param = hand.forward(img)
                if param:
                    angles[0] = np.mean(param[0]['angle'])  # Trung bình góc tay
                hand.draw2d(img, param)
                cv2.imshow('Hand', img)  # Window debug gesture
                cv2.waitKey(1)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                MENU_STATE = 'main'
                return
            elif event.type == KEYDOWN:
                # FIX: UP/DOWN + gesture (thả tay >55 = UP, nắm <30 = DOWN)
                if event.key == K_UP or (angles[0] > 55 if angles[0] else False):
                    selected_index = max(0, selected_index - 1)
                elif event.key == K_DOWN or (angles[0] < 30 if angles[0] else False):
                    selected_index = min(len(high_scores) - 1, selected_index + 1)
                elif event.key == K_RETURN and selected_index < len(high_scores):
                    MENU_STATE = 'delete_confirm'
                    confirmDelete(selected_index)
                    # Sau confirm, quay lại đây (state machine xử lý)
            elif event.type == MOUSEMOTION:  # FIX: Hover effect như difficultyMenu
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                else:
                    hover_index = -1
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # FIX: Click entry
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos) and i < len(high_scores):
                        selected_index = i
                        MENU_STATE = 'delete_confirm'
                        confirmDelete(i)
                        # Sau confirm, quay lại đây (state machine xử lý)

        # Vẽ bảng – FIX: Giống difficultyMenu, background + title English
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        title = font.render('High Scores', True, (255, 255, 255))  # FIX: English
        SCREEN.blit(title, (SCREENWIDTH // 2 - title.get_width() // 2, 100))

        if high_scores:
            button_rects = []  # FIX: Reset mỗi frame
            for i, entry in enumerate(high_scores):  # FIX: Loop vẽ button cho mỗi entry
                is_selected = (i == selected_index)
                is_hover = (i == hover_index)
                color = (255, 215, 0) if is_hover else (255, 255, 0) if is_selected else (255, 255, 255)  # FIX: Color như difficultyMenu
                text = small_font.render(f'{i+1}. {entry["name"]} - {entry["score"]}', True, color)  # FIX: English text rõ
                text_rect = text.get_rect(center=(SCREENWIDTH // 2, 250 + i * 60))  # FIX: y = 150 + i*40 (khoảng cách 40px cho entries ngắn)

                # FIX: Vẽ khung button bo tròn + hover scale
                scale = 1.1 if is_hover else 1.0
                button_width = int((text_rect.width + 40) * scale)
                button_height = int((text_rect.height + 20) * scale)
                button_rect = pygame.Rect(
                    SCREENWIDTH // 2 - button_width // 2, text_rect.y - 10,
                    button_width, button_height
                )
                pygame.draw.rect(SCREEN, (50, 50, 50), button_rect, border_radius=10)  # Nền xám bo tròn
                pygame.draw.rect(SCREEN, color, button_rect, 2, border_radius=10)  # Border color

                # FIX: Blit text (scale nếu hover)
                if is_hover:
                    scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                    scaled_rect = scaled_text.get_rect(center=text_rect.center)
                    SCREEN.blit(scaled_text, scaled_rect)
                else:
                    SCREEN.blit(text, text_rect)
                button_rects.append(button_rect)  # Lưu hitbox cho click/hover
        else:
            no_score = small_font.render('No scores yet!', True, (255, 0, 0))  # FIX: English
            SCREEN.blit(no_score, (SCREENWIDTH // 2 - no_score.get_width() // 2, 220))

        # FIX: Hướng dẫn English + gesture
        instr_lines = ['Select + Enter to delete', 'ESC to back']  # FIX: Split thành 2 dòng cho ngắn
        line_height = small_font.get_height() * 1.2  # FIX: Chiều cao dòng + spacing 20% (thoáng)
        y_base = 400  # FIX: Bắt đầu y=400 (cách entries ~60px)

        for i, line in enumerate(instr_lines):
            instr_text = small_font.render(line, True, (255, 255, 255))  # Render từng dòng
            instr_x = SCREENWIDTH // 2 - instr_text.get_width() // 2  # Căn giữa x
            instr_y = y_base + i * line_height  # FIX: y tăng dần cho mỗi dòng
            SCREEN.blit(instr_text, (instr_x, instr_y + 250))

        pygame.display.update()
        clock.tick(FPS)

def confirmDelete(index_to_delete):
    global high_scores
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('dejavusans', int(25 * SCALE_FACTOR), bold=True)  # DejaVuSans + scale cho UTF-8 English

    selected = 0  # Index button chọn: 0=Delete Entry, 1=Delete All, 2=Cancel
    options = ['Delete This Entry', 'Delete All', 'Cancel']  # FIX: Dịch sang English, ngắn gọn

    button_rects = []  # List rect cho mỗi button (cho hover/click)

    while True:
        mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột mỗi frame cho hover
        hover_index = -1  # Index button đang hover

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return  # Cancel, quay về highscore

            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    selected = (selected - 1) % len(options)  # Di chuyển lên
                elif event.key == K_DOWN:
                    selected = (selected + 1) % len(options)  # Di chuyển xuống
                elif event.key == K_RETURN:
                    handle_button_click(selected, index_to_delete)  # Xử lý chọn (hàm global)
                    return  # Thoát sau hành động

            elif event.type == pygame.MOUSEMOTION:  # Hover effect
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        hover_index = i
                        break
                    else:
                        hover_index = -1

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click trái
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        handle_button_click(i, index_to_delete)  # Xử lý click
                        return

        # Vẽ background và title
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        confirm_title = font.render('Delete this entry?', True, (255, 0, 0))  # FIX: English title
        SCREEN.blit(confirm_title, (SCREENWIDTH // 2 - confirm_title.get_width() // 2, 100))

        # Hiển thị entry đang xóa (an toàn với try-except)
        try:
            entry_text = font.render(f'{high_scores[index_to_delete]["name"]} - {high_scores[index_to_delete]["score"]}', True, (255, 255, 255))
        except IndexError:
            entry_text = font.render('Entry does not exist!', True, (255, 0, 0))  # FIX: English error
        SCREEN.blit(entry_text, (SCREENWIDTH // 2 - entry_text.get_width() // 2, 200))

        # Vẽ 3 buttons (cải thiện: bo tròn, hover scale, selected highlight)
        button_rects = []  # Reset mỗi frame
        for i, option in enumerate(options):
            is_selected = (i == selected)
            is_hover = (i == hover_index)
            color = (255, 0, 0) if is_selected else (255, 255, 0) if is_hover else (255, 255, 255)
            
            text = font.render(option, True, color)  # FIX: Render English option
            text_rect = text.get_rect(center=(SCREENWIDTH // 2, 300 + i * 80))

            # Button rect với hover scale
            scale = 1.05 if is_hover else 1.0
            button_width = int((text_rect.width + 40) * scale)
            button_height = int((text_rect.height + 20) * scale)
            button_x = SCREENWIDTH // 2 - button_width // 2
            button_y = text_rect.y - 10
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Vẽ button bo tròn, semi-transparent
            pygame.draw.rect(SCREEN, (50, 50, 50, 180), button_rect, border_radius=10)
            pygame.draw.rect(SCREEN, color, button_rect, 3, border_radius=10)

            # Blit text (scale nếu hover)
            if is_hover:
                scaled_text = pygame.transform.scale(text, (int(text.get_width() * scale), int(text.get_height() * scale)))
                scaled_rect = scaled_text.get_rect(center=text_rect.center)
                SCREEN.blit(scaled_text, scaled_rect)
            else:
                SCREEN.blit(text, text_rect)
            
            button_rects.append(button_rect)

        # Hướng dẫn (cải thiện: thêm mouse)
        instr = font.render('Arrow keys / Click to select', True, (255, 255, 255))  # FIX: English instr
        SCREEN.blit(instr, (SCREENWIDTH // 2 - instr.get_width() // 2, 650))

        pygame.display.update()
        clock.tick(FPS)

# Hàm phụ xử lý click (để tránh lặp code)
def handle_button_click(button_index, index_to_delete):
    global high_scores
    if button_index == 0:  # Xóa entry này
        try:
            entry_name = high_scores[index_to_delete]['name']

            # Xoá entry trong list
            del high_scores[index_to_delete]

            # Ghi lại danh sách mới vào file JSON
            with open("high_scores.json", "w", encoding="utf-8") as f:
                json.dump(high_scores, f, indent=4, ensure_ascii=False)

            print(f"Đã xóa {entry_name} thành công!")

            # Âm thanh xác nhận
            if not IS_MUTED:
                GAME_SOUNDS['swoosh'].play()

        except IndexError:
            print("Lỗi: Entry không tồn tại!")
        except Exception as e:
            print(f"Lỗi khi ghi file JSON: {e}")
    elif button_index == 1:  # Xóa tất cả
        confirm_all = True  # Có thể thêm sub-confirm nếu muốn, nhưng đơn giản
        if confirm_all:
            high_scores = []  # Clear list
            with open(HIGH_SCORES_FILE, 'w') as f:
                json.dump(high_scores, f)  # Save empty
            print("Đã xóa toàn bộ bảng xếp hạng!")
            if not IS_MUTED:
                GAME_SOUNDS['swoosh'].play()
    # button_index == 2: Hủy, không làm gì

if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by CodeWithHarry')

    load_high_scores()

    GAME_SPRITES['numbers'] = (
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

    GAME_SPRITES['message'] =pygame.image.load(r'gallery\sprites\message.png').convert_alpha()
    
    GAME_SPRITES['base'] = scale_image(pygame.image.load(r'gallery\sprites\base.png').convert_alpha(), SCALE_FACTOR)
    GAME_SPRITES['pipe'] = (
        scale_image(pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180), SCALE_FACTOR),
        scale_image(pygame.image.load(PIPE).convert_alpha(), SCALE_FACTOR)
    )
    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound(r'gallery\audio\die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound(r'gallery\audio\hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound(r'gallery\audio\point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound(r'gallery\audio\swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound(r'gallery\audio\wing.wav')

    GAME_SPRITES['background'] = scale_image(pygame.image.load(BACKGROUND).convert(), SCALE_FACTOR)
    GAME_SPRITES['player'] = scale_image(pygame.image.load(PLAYER).convert_alpha(), SCALE_FACTOR)
    score_from_game = 0  # Biến tạm

    while True:
        if MENU_STATE == 'main':
            mainMenu()
        elif MENU_STATE == 'difficulty':
            difficultyMenu()
        elif MENU_STATE == 'highscore':
            highScoreScreen()
        elif MENU_STATE == 'enter_name':
            # enterNameScreen(current_score)
            MENU_STATE = 'highscore'
        elif MENU_STATE == 'delete_confirm':
            confirmDelete(selected_index)
            MENU_STATE = 'highscore'
        elif MENU_STATE == 'playing':
            curent_score = mainGame()
            MENU_STATE = 'enter_name'  # Sau chơi, quay về menu