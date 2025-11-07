from global_variables import *
import cv2
import sys
import random
import pygame
import numpy as np
import json
import os
from pygame.locals import * 

# Hàm dùng để tạo 2 ống trên và ống dưới
def getRandomPipe():
    pipeHeight = gv.GAME_SPRITES['pipe'][0].get_height()
    offset = int(gv.DIFFICULTY_LEVELS[current_difficulty]['gap_offset'])
    y2 = offset + random.randrange(0, int(gv.SCREENHEIGHT - gv.GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = gv.SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]
    
    return pipe