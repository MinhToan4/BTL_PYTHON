
import pygame

from global_variables import *

def scale_image(image, factor):
    width = int(image.get_width() * factor)
    height = int(image.get_height() * factor)
    return pygame.transform.scale(image, (width, height))
