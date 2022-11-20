import os
import time
import pygame
import socket
import string
from OfflineGame import *
from OnlineGame import *
from Constants import *


IP = '0.0.0.0'
PORT = 55555


def login_screen(screen):
    message = ["", "", ""]
    finish = False
    while not finish:
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\LoginScreen.png"), (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if 505 < mouse_pos[0] < 700 and \
                            220 < mouse_pos[1] < 270:
                        message[0] = "SGNIN"
                        finish = True
                    elif 495 < mouse_pos[0] < 705 and \
                            305 < mouse_pos[1] < 355:
                        message[0] = "SGNUP"
                        finish = True
    return message


def connect_screen(sock, screen, message):
    success = False
    while not success:
        text_box = 1
        font = pygame.font.Font(os.getcwd() + "\\Fonts\\BERNHC.ttf", 55)
        finish = False
        while not finish:
            screen.blit(pygame.image.load(os.getcwd() + "\\Images\\CreateAccount.png"), (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if 195 < mouse_pos[0] < 1030 and \
                                100 < mouse_pos[1] < 165:
                            text_box = 1
                        elif 195 < mouse_pos[0] < 1030 and \
                                270 < mouse_pos[1] < 340:
                            text_box = 2
                        elif 965 < mouse_pos[0] < 1155 and \
                                440 < mouse_pos[1] < 475:
                            finish = True
                        else:
                            text_box = 3
                elif event.type == pygame.KEYDOWN and text_box != 3:
                    if event.key == pygame.K_BACKSPACE and message[text_box] != "":
                        message[text_box] = message[text_box][:len(message[text_box]) - 1]
                    elif event.key == pygame.K_TAB:
                        text_box = text_box + 1 if text_box < 3 else text_box
                    elif pygame.key.name(event.key) in string.digits + string.ascii_lowercase:
                        if len(message[text_box]) < 30:
                            message[text_box] += pygame.key.name(event.key)
                    elif event.key == pygame.K_RETURN:
                        finish = True
            text = font.render(message[1], True, (255, 255, 255))
            screen.blit(text, (205, 100))
            text = font.render(message[2], True, (225, 255, 255))
            screen.blit(text, (205, 270))
            pygame.display.flip()

        message = "~".join(message)
        sock.sendto(message.encode(), (SRV_IP, SRV_PORT))
        message = message.split("~")

        data, addr = sock.recvfrom(200)
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\CreateAccount.png"), (0, 0))
        data = data.decode("UTF8").split("~")
        if data[0] == "LOGIN":
            if bool(int(data[1])):
                success = True
            else:
                text = "Login failed - username or password are incorrect. try again."
                font = pygame.font.Font(os.getcwd() + "\\Fonts\\BERNHC.ttf", 20)
                text = font.render(text, True, (200, 0, 0))
                screen.blit(text, (150, 440))
                pygame.display.flip()
                time.sleep(5)
        elif data[0] == "REGIS":
            if bool(int(data[1])):
                message[0] = "SGNIN"
                message[1] = ""
                message[2] = ""
                text = "You have successfully registered - you must now enter your username and password."
                font = pygame.font.Font(os.getcwd() + "\\Fonts\\BERNHC.ttf", 20)
                text = font.render(text, True, (0, 150, 0))
                screen.blit(text, (150, 440))
                pygame.display.flip()
                time.sleep(5)
            else:
                message[1] = ""
                message[2] = ""
                text = "Registration failed - username or password incorrect. Try again."
                font = pygame.font.Font(os.getcwd() + "\\Fonts\\BERNHC.ttf", 20)
                text = font.render(text, True, (200, 0, 0))
                screen.blit(text, (150, 440))
                pygame.display.flip()
                time.sleep(5)


def opening_screen(sock, screen):
    message = ""
    finish = False
    while not finish:
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\OpeningScreen.png"), (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if 310 < mouse_pos[0] < 890 and \
                        130 < mouse_pos[1] < 195:
                    message = "ONGAM"
                    finish = True
                elif 300 < mouse_pos[0] < 900 and \
                        245 < mouse_pos[1] < 305:
                    message = "OFGAM"
                    finish = True
                elif 445 < mouse_pos[0] < 755 and \
                        350 < mouse_pos[1] < 400:
                    instructions(screen)
    if message == "ONGAM":
        sock.sendto(message.encode(), (SRV_IP, SRV_PORT))
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\StandbyScreen.png"), (0, 0))
        pygame.display.flip()
        data, addr = sock.recvfrom(200)
        finish = data.decode("UTF8")
        while finish != "START":
            data, addr = sock.recvfrom(200)
            finish = data.decode("UTF8")
        return "online_game"
    elif message == "OFGAM":
        sock.sendto(message.encode(), (SRV_IP, SRV_PORT))
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\Standby.png"), (0, 0))
        pygame.display.flip()
        data, addr = sock.recvfrom(200)
        finish = data.decode("UTF8")
        while finish != "BEGIN":
            data, addr = sock.recvfrom(200)
            finish = data.decode("UTF8")
        return "offline_game"


def instructions(screen):
    count = 1
    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if count == 2:
                    finish = True
                else:
                    count += 1
        screen.blit(pygame.image.load(os.getcwd() + "\\Images\\Instructions" + str(count) + ".png"), (0, 0))
        pygame.display.flip()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size)
    icon = pygame.image.load(os.getcwd() + "\\Images\\Icon.png").convert()
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Rock Hero")

    message = login_screen(screen)
    connect_screen(sock, screen, message)
    game_type = opening_screen(sock, screen)
    if game_type == "online_game":
        online_game(sock, screen)
    elif game_type == "offline_game":
        offline_game(screen)
    pygame.quit()


if __name__ == '__main__':
    main()
