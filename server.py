import socket
import threading
from json import dumps, loads
from typing import Dict, List, Tuple
from database import Database


SERVER_ADDRESS = ("127.0.0.1", 8080)
MAX_PACKAGE_SIZE = 4096


class Server:
    def __init__(self, server_address : Tuple[str, int], max_package_size : int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(server_address)
        self.server.listen()

        self.running = True
        self.max_package_size = max_package_size

        self.online_users : Dict[str, socket.socket] = {}

        print(f"[*] Server set up on {server_address}")

    def run(self):
        print("[*] Server is listening for connections")
        while self.running:
            client, addr = self.server.accept()
            threading.Thread(target=self.connection_handler, args=(client, )).start()
            print(f"[+] User {addr} has connected to server")

    def connection_handler(self, client : socket.socket):
        username = None
        db = Database("Raziel")

        try:
            while True:
                data : List = loads(client.recv(self.max_package_size).decode())
                scode = data[0]
                if scode == "LOGIN":
                    if not db.check_if_user_exists(data[1]):
                        client.send(dumps(["STATUS", "USER_DOES_NOT_EXIST"]).encode())
                    elif db.get_user_password(data[1]) != data[2]:
                        client.send(dumps(["STATUS", "INCORRECT_PASSWORD"]).encode())
                    else:
                        username = data[1]
                        self.online_users[data[1]] = client #<---- Может вызвать проблемы
                        client.send(dumps(["STATUS", "SUCCESS"]).encode())
                elif scode == "REGISTER":
                    if db.check_if_user_exists(data[1]):
                        client.send(dumps(["STATUS", "USERNAME_IS_ALREADY_TAKEN"]).encode())
                    else:
                        db.add_user(data[1], data[2])
                        username = data[1]
                        self.online_users[data[1]] = client #<---- Может вызвать проблемы
                        client.send(dumps(["STATUS", "SUCCESS"]).encode())
                elif scode == "GET_MESSAGE_HISTORY":
                    history = db.load_message_history(data[1], data[2])
                    client.send(dumps(["MESSAGE_HISTORY", history]).encode())
                elif scode == "DELETE_MESSAGE_HISTORY":
                    db.delete_message_history(data[1], data[2])
                elif scode == "SEND_MESSAGE":
                    db.add_message(data[1], data[2], data[3])
                    if self.online_users.get(data[2], 0) != 0:
                        self.online_users[data[2]].send(dumps(["MESSAGE", data[1], data[3]]).encode())
                elif scode == "REGISTER_CHECK":
                    client.send(dumps(["REGISTER_CHECK", db.check_if_user_exists(data[1])]).encode())
                elif scode == "FRIENDS":
                    client.send(dumps(["FRIENDS", db.get_user_friends(data[1])]).encode())
                elif scode == "DELETE_ACCOUNT":
                    db.delete_user(data[1])
                else:
                    print(f'[?] Unknown request: {scode}')


        except ConnectionResetError:
            print("[-] User has disconnected from server")
            self.online_users.pop(username, None)
        except Exception as e:
            print(f"[!] Something went wrong: {e}")
            self.online_users.pop(username, None)
            print("[!] User was forcibly disconnected")

        db.close_connection()


if __name__ == "__main__":
    Server(SERVER_ADDRESS, MAX_PACKAGE_SIZE).run()
