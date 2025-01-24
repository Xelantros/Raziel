import threading
from customtkinter import *
import socket
import sys
from json import dumps, loads
from typing import Tuple, List
from frames import LoginFrame, RegisterFrame, MainFrame


set_appearance_mode("dark")
set_default_color_theme("blue")


VERSION = "0.0.1"
SERVER_ADDRESS = ("127.0.0.1", 8080)


class App(CTk):
    def __init__(self, version : str, server_address : Tuple[str, int]):
        super().__init__()

        self.version = version

        self.client : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(server_address)

        self.username = None
        self.current_chat = None

        threading.Thread(target=self.server_answers_handler, daemon=True).start()
        self.server_answer = None

        base_width = 600
        base_height = 400

        spawn_x = (self.winfo_screenwidth() - base_width) // 2
        spawn_y = (self.winfo_screenheight() - base_height) // 2

        self.geometry(f"{base_width}x{base_height}+{spawn_x}+{spawn_y - 100}")
        self.minsize(600, 400)
        self.title(f"Raziel v{self.version}")

        self.main_frame = LoginFrame(self)
        self.main_frame.pack(expand=True, fill="both")

    def open_main_frame(self):
        self.main_frame.destroy()
        self.main_frame = MainFrame(self)
        self.main_frame.pack(expand=True, fill="both")

    def open_login_frame(self):
        self.main_frame.destroy()
        self.main_frame = LoginFrame(self)
        self.main_frame.pack(expand=True, fill="both")

    def open_register_frame(self):
        self.main_frame.destroy()
        self.main_frame = RegisterFrame(self)
        self.main_frame.pack(expand=True, fill="both")

    def send_message(self, text):
        self.main_frame.textbox.configure(state="normal")
        self.main_frame.textbox.insert("end", f"{self.username}: {text}\n")
        self.main_frame.textbox.configure(state="disabled")
        self.main_frame.textbox.yview("end")
        self.client.send(dumps(["SEND_MESSAGE", self.username, self.current_chat, text]).encode())

    def request_deletion_of_message_history(self, username : str):
        self.client.send(dumps(["DELETE_MESSAGE_HISTORY", self.username, username]).encode())

    def get_message_history(self, username) -> List[Tuple[str, str, str, str]]:
        self.client.send(dumps(["GET_MESSAGE_HISTORY", self.username, username]).encode())
        while True:
            if self.server_answer is not None:
                temp = self.server_answer
                self.server_answer = None
                return temp

    def request_friends_list(self):
        self.client.send(dumps(["FRIENDS", self.username]).encode())
        while True:
            if self.server_answer is not None:
                temp = self.server_answer
                self.server_answer = None
                return temp

    def login(self, username : str, password : str) -> str:
        self.client.send(dumps(["LOGIN", username, password]).encode())
        while True:
            if self.server_answer is not None:
                temp = self.server_answer
                self.server_answer = None
                return temp

    def logout(self):
        self.username = None
        self.current_chat = None
        self.server_answer = None
        self.open_login_frame()

    def check_if_user_is_registered(self, username):
        self.client.send(dumps(["REGISTER_CHECK", username]).encode())
        while True:
            if self.server_answer is not None:
                temp = self.server_answer
                self.server_answer = None
                return temp

    def sign_up(self, username : str, password : str) -> str:
        self.client.send(dumps(["REGISTER", username, password]).encode())
        while True:
            if self.server_answer is not None:
                temp = self.server_answer
                self.server_answer = None
                return temp

    def server_answers_handler(self):
        while True:
            data = loads(self.client.recv(4096).decode())
            scode = data[0]
            if scode == "STATUS" or scode == "MESSAGE_HISTORY" or scode == "REGISTER_CHECK" or scode == "FRIENDS":
                self.server_answer = data[1]
            elif scode == "MESSAGE":
                if self.current_chat == data[1] and self.main_frame.name == "MainFrame":
                    self.main_frame.textbox.configure(state="normal")
                    self.main_frame.textbox.insert("end", f"{data[1]}: {data[2]}\n")
                    self.main_frame.textbox.configure(state="disabled")
            else:
                raise ValueError


if __name__ == "__main__":

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 65432))
    except socket.error:
        sys.exit()

    app = App(VERSION, SERVER_ADDRESS)
    app.mainloop()
