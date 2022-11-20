import pygame
import os
import time
import random
import threading
from Life import *
from Arrow import *
from Constants import *

arrows_player = pygame.sprite.Group()
arrows_enemy = pygame.sprite.Group()
explosion = [[], []]
create_arrow = []
messages = []


def game_music(type_music):
    music = [os.getcwd() + "\\Music\\Alice Cooper - School's Out.mp3",
             os.getcwd() + "\\Music\\Poison - Talk Dirty To Me.mp3",
             os.getcwd() + "\\Music\\The Strokes - Reptilia.mp3",
             os.getcwd() + "\\Music\\Priestess - Lay Down.mp3",
             os.getcwd() + "\\Music\\The Who - The Seeker.mp3"]
    pygame.mixer.init()
    pygame.mixer.music.load(music[type_music])
    pygame.mixer.music.play()


def player_keys(sock, key, player_life):
    global arrows_player
    global explosion
    keys = [pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT]
    is_explode = False
    for arrow in arrows_player.sprites():
        if 435 <= arrow.ypos <= 485:
            if key == keys[arrow.type]:
                explosion[0] = [arrow.image_explode, (arrow.xpos - 9, 443)]
                arrow.kill()
                is_explode = True
                sock.sendto(("PRESS~" + str(int(True))).encode(), (SRV_IP, SRV_PORT))
    if not is_explode:
        player_life.remove_life("HeartHalfLife")
        sock.sendto(("PRESS~" + str(int(False))).encode(), (SRV_IP, SRV_PORT))


def enemy_keys(data, enemy_life):
    global arrows_enemy
    global explosion
    if data:
        for arrow in arrows_enemy.sprites():
            if 440 <= arrow.ypos:
                explosion[1] = [arrow.image_explode, (arrow.xpos - 9, 443)]
                arrow.kill()
    else:
        enemy_life.remove_life("HeartHalfLife")


def explode(screen, count, position):
    global explosion
    if count == 20:
        explosion[position] = []
        count = 0
    elif explosion:
        if len(explosion[position]) != 0:
            screen.blit(explosion[position][0], explosion[position][1])
            count += 1
    return count


def miss_arrow(sock, arrows, life):
    for arrow in arrows.sprites():
        if arrow.ypos > 500:
            arrow.kill()
            life.remove_life("HeartDeath")
            if arrows == arrows_player:
                if life.hearts != 0:
                    sock.sendto(("MISSA~" + str(int(True))).encode(), (SRV_IP, SRV_PORT))
                else:
                    sock.sendto(("MISSA~" + str(int(False))).encode(), (SRV_IP, SRV_PORT))


def update(screen, background, player_life, enemy_life, count):
    global arrows_player
    global arrows_enemy
    screen.blit(background, (0, 0))
    screen.blit(background, (600, 0))
    player_life.print_life()
    enemy_life.print_life()
    if count == 30:
        if len(create_arrow) != 0:
            type_arrow = create_arrow.pop(0)
            arrow = Arrow(type_arrow, 6, screen, 298, "Player")
            arrows_player.add(arrow)
            arrow = Arrow(type_arrow, 6, screen, 898, "Enemy")
            arrows_enemy.add(arrow)
            count = 0
    else:
        count += 1
    arrows_player.update()
    arrows_enemy.update()
    return count


def quite(sock, addr):
    sock.sendto("QUITE".encode(), addr)
    message = [""]
    while message[0] != "ENDED":
        if len(messages) != 0:
            message = messages.pop(0)
    pygame.mixer.music.stop()
    return bool(int(message[1]))


def end_game(screen, is_winner):
    if is_winner:
        victory = pygame.image.load(os.getcwd() + "\\Images\\VictoryScreen.png")
        screen.blit(victory, (0, 0))
        pygame.mixer.music.stop()
        pygame.display.flip()
        time.sleep(2.5)
    else:
        defeat = pygame.image.load(os.getcwd() + "\\Images\\DefeatScreen.png")
        screen.blit(defeat, (0, 0))
        pygame.mixer.music.stop()
        pygame.display.flip()
        time.sleep(2.5)


def online_game(sock, screen):
    global arrows_player
    global arrows_enemy

    clock = pygame.time.Clock()
    background = pygame.image.load(os.getcwd() + "\\Images\\Background.png")

    player_life = Life(screen, 10, 10)
    enemy_life = Life(screen, 610, 10)

    data, addr = sock.recvfrom(200)
    type_music = data.decode("UTF8").split("~")
    while type_music[0] != "GSONG":
        data, addr = sock.recvfrom(200)
        type_music = data.decode("UTF8").split("~")
    game_music(int(type_music[1]))

    t = threading.Thread(target=handle_online_game, args=(sock,))
    t.start()

    count_create_arrow = 0
    count_player_explode = 0
    count_enemy_explode = 0

    finish = False
    while not finish:
        miss_arrow(sock, arrows_player, player_life)
        count_create_arrow = update(screen, background, player_life, enemy_life, count_create_arrow)
        count_player_explode = explode(screen, count_player_explode, 0)
        count_enemy_explode = explode(screen, count_enemy_explode, 1)
        if player_life.hearts <= 0:
            end_game(screen, quite(sock, addr))
            finish = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game(screen, quite(sock, addr))
                finish = True
            elif event.type == pygame.KEYDOWN:
                player_keys(sock, event.key, player_life)
        if len(messages) != 0:
            message = messages.pop(0)
            if message[0] == "EMISS":
                miss_arrow(sock, arrows_enemy, enemy_life)
            elif message[0] == "ENKEY":
                enemy_keys(bool(int(message[1])), enemy_life)
            elif message[0] == "ENDED":
                end_game(screen, bool(int(message[1])))
                finish = True
        pygame.display.flip()
        clock.tick(FPS)
    t.join()


def handle_online_game(sock):
    finish = False
    while not finish:
        data, addr = sock.recvfrom(200)
        data = data.decode("UTF8").split("~")
        if data[0] == "ARROW":
            create_arrow.append(data[1])
        elif data[0] == "EMISS":
            messages.append(data)
        elif data[0] == "ENKEY":
            messages.append(data)
        elif data[0] == "ENDED":
            messages.append(data)
            finish = True
