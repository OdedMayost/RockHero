import pygame
import os
import time
import random
from Life import *
from Arrow import *
from Score import *
from Constants import *

arrows = pygame.sprite.Group()
explosion = []


def game_music():
    music = [os.getcwd() + "\\Music\\Alice Cooper - School's Out.mp3",
             os.getcwd() + "\\Music\\Poison - Talk Dirty To Me.mp3",
             os.getcwd() + "\\Music\\The Strokes - Reptilia.mp3",
             os.getcwd() + "\\Music\\Priestess - Lay Down.mp3",
             os.getcwd() + "\\Music\\The Who - The Seeker.mp3"]
    type_music = random.randint(0, 4)
    pygame.mixer.init()
    pygame.mixer.music.load(music[type_music])
    pygame.mixer.music.play()


def game_keys(key, player_life, score):
    global arrows
    global explosion
    keys = [pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT]
    is_explode = False
    for arrow in arrows.sprites():
        if 435 <= arrow.ypos <= 485:
            if key == keys[arrow.type]:
                explosion = [arrow.image_explode, (arrow.xpos - 9, 443)]
                arrow.kill()
                score.add_score(100)
                is_explode = True
    if not is_explode:
        player_life.remove_life("HeartHalfLife")


def explode(screen, count):
    global explosion
    if count == 20:
        count = 0
        explosion = []
    elif explosion:
        screen.blit(explosion[0], explosion[1])
        count += 1
    return count


def miss_arrow(player_life):
    global arrows
    for arrow in arrows.sprites():
        if arrow.ypos > 500:
            arrow.kill()
            player_life.remove_life("HeartDeath")


def update(screen, player_life, background, score, count):
    global arrows
    screen.fill((0, 0, 0))
    screen.blit(background, (300, 0))
    player_life.print_life()
    score.print_score()
    if count == 28:
        type_arrow = random.randint(0, 3)
        arrow = Arrow(type_arrow, 7, screen, 598, "Player")
        arrows.add(arrow)
        count = 0
    else:
        count += 1
    arrows.update()
    return count


def offline_game(screen):
    global arrows
    clock = pygame.time.Clock()
    background = pygame.image.load(os.getcwd() + "\\Images\\Background.png")
    player_life = Life(screen, 310, 10)
    score = Score(screen, 310, 60)
    game_music()
    count_create_arrow = 0
    count_explode = 0

    finish = False
    while not finish:
        miss_arrow(player_life)
        count_create_arrow = update(screen, player_life, background, score, count_create_arrow)
        count_explode = explode(screen, count_explode)
        pygame.display.flip()
        clock.tick(FPS)
        if player_life.hearts <= 0:
            defeat = pygame.image.load(os.getcwd() + "\\Images\\DefeatScreen.png")
            screen.blit(defeat, (0, 0))
            pygame.mixer.music.stop()
            pygame.display.flip()
            time.sleep(5)
            finish = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
            elif event.type == pygame.KEYDOWN:
                game_keys(event.key, player_life, score)
