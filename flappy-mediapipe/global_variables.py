# Tạo các biến toàn bộ cho các tệp trong gói

import pygame
import global_variables as gv
import os

SCALE_FACTOR = 1.5
FPS = 32
FPSCLOCK = None
SCREENWIDTH = int(289 *SCALE_FACTOR)
SCREENHEIGHT = int(511 * SCALE_FACTOR)
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
IS_MUTED = False 
GOD_MODE = False 
PLAYER = r'gallery\sprites\bird.png'
BACKGROUND = r'gallery\sprites\background.png'
PIPE = r'gallery\sprites\pipe.png'
MENU_STATE = 'main'  # Các trạng thái màn hình: 'main', 'difficulty', 'highscore', 'playing'
DIFFICULTY_LEVELS = {
    'Easy': {'pipe_vel_x': -3, 'gap_offset': SCREENHEIGHT / 3 * 1.5},  # Chậm, gap rộng
    'Medium': {'pipe_vel_x': -4, 'gap_offset': SCREENHEIGHT / 3},      # Mặc định
    'Hard': {'pipe_vel_x': -6, 'gap_offset': SCREENHEIGHT / 3 * 0.8}   # Nhanh, gap hẹp
}
# Sử dụng đường dẫn tuyệt đối dựa trên vị trí file này
HIGH_SCORES_FILE = os.path.join(os.path.dirname(__file__), 'highscores.json')
high_scores = []
MAX_NAME_LENGTH = 10  # Giới hạn tên nhập
# current_difficulty = os.environ.get('DIFFICULTY', 'Medium')
current_difficulty = 'Medium'  # Mặc định
current_score = 0
selected_index = 0

MENU_FADE_ALPHA = 255  # Alpha cho title fade-in (bắt đầu mờ)
BIRD_ANIM_ANGLE = 0  # Góc xoay chim idle
BIRD_FLAP_FRAME = 0
cap = None
using_mock = False
hand = None