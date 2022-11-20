import pygame
import os
from Constants import *


class Score(pygame.sprite.Sprite):
    def __init__(self, screen, xpos, ypos):
        self.ypos = ypos
        self.xpos = xpos
        self.score = 0
        self.screen = screen
        self.font = pygame.font.Font(os.getcwd() + "\\Fonts\\Revolvingdor.otf", 20)

    def add_score(self, value):
        self.score += 500

    def print_score(self):
        text = self.font.render("Score: " + str(self.score), True, (125, 50, 250))
        self.screen.blit(text, (self.xpos, self.ypos))

