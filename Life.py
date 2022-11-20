import pygame
import os
from Constants import *


class Life(pygame.sprite.Sprite):
    def __init__(self, screen, xpos, ypos):
        self.ypos = ypos
        self.xpos = xpos
        self.heart_life = pygame.image.load(os.getcwd() + "\\Images\\HeartLife.png")
        self.heart_life.set_colorkey(TRANSPARENT_COLOR)
        self.heart_half_life = pygame.image.load(os.getcwd() + "\\Images\\HeartHalfLife.png")
        self.heart_half_life.set_colorkey(TRANSPARENT_COLOR)
        self.heart_death = pygame.image.load(os.getcwd() + "\\Images\\HeartDeath.png")
        self.heart_death.set_colorkey(TRANSPARENT_COLOR)
        self.max_hearts = 3 * 2
        self.hearts = self.max_hearts
        self.screen = screen

    def remove_life(self, type):
        if type == "HeartHalfLife":
            self.hearts -= 1
        elif type == "HeartDeath":
            self.hearts -= 2

    def print_life(self):
        i = self.hearts
        x = self.xpos
        while i > (self.hearts - self.max_hearts) / 2 * 2:
            if i > 1:
                self.screen.blit(self.heart_life, (x, self.ypos))
            elif i == 1:
                self.screen.blit(self.heart_half_life, (x, self.ypos))
            elif i <= 0:
                self.screen.blit(self.heart_death, (x, self.ypos))
            x += 60
            i -= 2

