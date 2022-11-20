import pygame
import os
from Constants import *


class Arrow(pygame.sprite.Sprite):
    def __init__(self, type, velocity, screen, position, type_explosion):
        pygame.sprite.Sprite.__init__(self)
        types = ["Left", "Up", "Down", "Right"]
        self.type = int(type)
        self.xpos = position + self.type * 70
        self.ypos = -50
        self.image = pygame.image.load(os.getcwd() + "\\Images\\%s" % types[self.type] + "Arrow.png")
        self.image.set_colorkey(TRANSPARENT_COLOR)
        self.image_explode = pygame.image.load(os.getcwd() + "\\Images\\%s" % types[self.type] +
                                               type_explosion + "Explosion.png")
        self.velocity = velocity
        self.screen = screen

    def update(self):
        self.ypos += self.velocity
        self.screen.blit(self.image, (self.xpos, self.ypos))

