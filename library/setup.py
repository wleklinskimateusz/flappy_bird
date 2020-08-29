import pygame
import neat
import time
import os
import random
from library.Bird import Bird
from library.Base import Base
from library.Player import Player
from library.Pipe import Pipe
pygame.font.init()
pygame.mixer.init()



def load_file(name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", name + ".png")))

def distance(x1, y1, x2, y2):
    d = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
    return d

def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()
