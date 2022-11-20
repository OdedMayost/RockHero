import socket
import threading
import hashlib
import random
import time

IP = '0.0.0.0'
PORT = 50000

clients = {}  # key - client's address, value - list of messages to send
clients_lock = threading.Lock()
users = {}  # key - client's address, value - another player (enemy)
users_lock = threading.Lock()
game_mode = {}  # key -  client's address, value - Is the player in the game
game_mode_lock = threading.Lock()
connect = None
connect_lock = threading.Lock()


def create_account(username, password):
    accounts = {}
    with open("Users.txt") as file:
        for line in file:
            user = line.strip().split(":")
            accounts[user[0]] = user[1]

    if username not in accounts.keys():
        password = hashlib.sha256(password.encode()).hexdigest()
        with open("Users.txt", "a") as file:
            file.write(username + ":" + password + "\n")
        return True
    else:
        return False


def login_account(username, password):
    accounts = {}
    with open("Users.txt") as file:
        for line in file:
            user = line.strip().split(":")
            accounts[user[0]] = user[1]

    if username in accounts.keys():
        password = hashlib.sha256(password.encode()).hexdigest()
        if password == accounts[username]:
            return True
        else:
            return False
    else:
        return False


def connect_player(addr):
    global connect
    creator = None
    connect_lock.acquire()
    if connect is None:
        connect = addr
        creator = True
    else:
        users_lock.acquire()
        users[addr] = connect
        users[connect] = addr
        creator = False
        connect = None
        users_lock.release()
    connect_lock.release()
    while connect == addr:
        pass

    clients_lock.acquire()
    users_lock.acquire()
    if clients[addr][0] != "GSONG":
        type_music = random.randint(0, 4)
        clients[addr] = ["GSONG", str(type_music)]
        clients[users[addr]] = ["GSONG", str(type_music)]
    users_lock.release()
    clients_lock.release()

    time_now = round(time.time() * 1000)
    game_mode_lock.acquire()
    game_mode[addr] = ["online_game", time_now, creator]
    game_mode_lock.release()

    return "START"


def quite(addr, type):
    if type:
        clients_lock.acquire()
        if addr in clients.keys():
            clients.pop(users[addr])
            clients.pop(addr)
        clients_lock.release()
        game_mode_lock.acquire()
        if addr in game_mode.keys():
            game_mode.pop(users[addr])
            game_mode.pop(addr)
        game_mode_lock.release()
        users_lock.acquire()
        if addr in users.keys():
            users.pop(users[addr])
            users.pop(addr)
        users_lock.release()
    else:
        clients_lock.acquire()
        if addr in clients.keys():
            clients.pop(addr)
        clients_lock.release()
        users_lock.acquire()
        if addr in users.keys():
            users.pop(addr)
        users_lock.release()
        game_mode_lock.acquire()
        if addr in game_mode.keys():
            game_mode.pop(addr)
        game_mode_lock.release()


def create_arrow(addr, time_arrow):
    time_now = round(time.time() * 1000)
    if (time_now - time_arrow) >= 600:
        type_arrow = random.randint(0, 3)
        message = ["ARROW", str(type_arrow)]
        clients_lock.acquire()
        clients[addr] = message
        clients[users[addr]] = message
        clients_lock.release()
        return time_now
    else:
        return time_arrow


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    threads = []
    while True:
        data, addr = sock.recvfrom(200)
        if addr not in clients.keys():
            clients_lock.acquire()
            clients[addr] = []
            clients_lock.release()
            t = threading.Thread(target=client, args=(sock, addr))
            t.start()
            threads.append(t)
            handle_message(addr, data)
        else:
            handle_message(addr, data)
    for t in threads:
        t.join()


def handle_message(addr, data):
    clients_lock.acquire()
    clients[addr] = data.decode("UTF8").split("~")
    clients_lock.release()


def client(sock, addr):
    while True:
        if addr in clients.keys():
            if len(clients[addr]) != 0:
                if clients[addr][0] == "SGNUP":
                    message = "REGIS~" + str(int(create_account(clients[addr][1], clients[addr][2])))
                    sock.sendto(message.encode(), addr)
                    clients[addr] = []
                elif clients[addr][0] == "SGNIN":
                    message = "LOGIN~" + str(int(login_account(clients[addr][1], clients[addr][2])))
                    sock.sendto(message.encode(), addr)
                    clients[addr] = []
                elif clients[addr][0] == "ONGAM":
                    sock.sendto(connect_player(addr).encode(), addr)
                elif clients[addr][0] == "OFGAM":
                    sock.sendto("BEGIN".encode(), addr)
                    clients[addr] = []
                    quite(addr, False)
                    return None
                elif clients[addr][0] == "MISSA":
                    if not bool(int(clients[addr][1])):
                        sock.sendto(("ENDED~" + str(int(False))).encode(), addr)
                        sock.sendto(("ENDED~" + str(int(True))).encode(), users[addr])
                        clients[addr] = []
                        quite(addr, True)
                        return None
                    else:
                        sock.sendto("EMISS".encode(), users[addr])
                        clients[addr] = []
                elif clients[addr][0] == "PRESS":
                    message = "ENKEY~" + clients[addr][1]
                    sock.sendto(message.encode(), users[addr])
                    clients[addr] = []
                elif clients[addr][0] == "QUITE":
                    sock.sendto(("ENDED~" + str(int(False))).encode(), addr)
                    sock.sendto(("ENDED~" + str(int(True))).encode(), users[addr])
                    clients[addr] = []
                    quite(addr, True)
                    return None

                elif clients[addr][0] == "GSONG":
                    sock.sendto(("~".join(clients[addr])).encode(), addr)
                    clients[addr] = []
                elif clients[addr][0] == "ARROW":
                    sock.sendto(("~".join(clients[addr])).encode(), addr)
                    clients[addr] = []

        game_mode_lock.acquire()
        if addr in game_mode.keys():
            if game_mode[addr][0] == "online_game" and game_mode[addr][2]:
                game_mode[addr][1] = create_arrow(addr, game_mode[addr][1])
        game_mode_lock.release()


if __name__ == '__main__':
    main()
