from customtkinter import *
from PIL import Image


class MainFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = "MainFrame"

        self.main_frame = CTkFrame(master=self)
        self.main_frame.pack(expand=True, fill="both")

        # Left

        self.lww = 200

        self.left_frame = CTkFrame(master=self.main_frame, width=self.lww)
        self.left_frame.pack(fill="y", side="left")

        self.add_btn = CTkButton(master=self.left_frame, width=self.lww, height=20, text="Добавить друга", command=self.add_friend)
        self.add_btn.pack(side="top", fill="x", padx=5, pady=5)

        self.scroll_frame = CTkScrollableFrame(master=self.left_frame, width=self.lww)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.button_frame = CTkFrame(master=self.left_frame, width=self.lww, height=40)
        self.button_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        self.logout_btn = CTkButton(self.button_frame, width=self.lww // 2, height=40, text="Выход", command=self.master.logout)
        self.logout_btn.pack(side="left", padx=5, pady=5)

        self.settings_btn = CTkButton(self.button_frame, width=self.lww // 2, height=40, text="Настройки", command=self.master.open_settings_frame)
        self.settings_btn.pack(side="left", padx=5, pady=5)

        # Right

        self.right_frame = CTkFrame(master=self.main_frame)
        self.right_frame.pack(fill="both", expand=True)

        self.cur_chat_lbl = CTkLabel(master=self.right_frame, height=20, text="", anchor="w")
        self.cur_chat_lbl.pack(side="top", fill="x", padx=5, pady=5)

        self.textbox = CTkTextbox(master=self.right_frame)
        self.textbox.configure(state="disabled")
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.msg_entry = CTkEntry(master=self.right_frame, height=50)
        self.msg_entry.bind(sequence="<Return>", command=self.send_message_wrapper)
        self.msg_entry.pack(side="bottom", fill="x", padx=5, pady=5)

        self.display_friends_buttons()


    def clear_textbox(self):
        self.textbox.configure(state="normal")
        self.textbox.delete(0.0, "end")
        self.textbox.configure(state="disabled")


    def add_friend(self):
        dialog = CTkInputDialog(text="Введите имя друга:", title="Add friend")
        content = dialog.get_input()

        if content and content != self.master.username and self.master.check_if_user_is_registered(content) and content not in self.master.friends_list:
            self.master.friends_list.append(content)
            self.create_full_friend_button(content)
        else:
            pass
            #Сообщить, что такого юзера нет при помощи инфобокса

    def create_full_friend_button(self, friend_username):
        friend_btn = CTkButton(master=self.scroll_frame,
                               height=30,
                               corner_radius=0,
                               fg_color="#33322d",
                               text=friend_username,
                               anchor="w",
                               command=lambda: self.open_chat(friend_username))  # <--- Подсказка нейросети
        friend_btn.pack(fill="x")

        delete_friend_btn = CTkButton(master=friend_btn,
                                      width=30,
                                      height=30,
                                      text="D",
                                      fg_color="red",
                                      command=lambda: self.delete_friend(friend_btn, friend_username))
        delete_friend_btn.place(x=self.lww - 30, y=0)  # <-------- Костыль!


    def delete_friend(self, button : CTkButton, username : str) -> None:
        button.destroy()
        self.master.friends_list.remove(username)
        self.master.request_deletion_of_message_history(username)
        if self.master.current_chat == username:
            self.master.current_chat = None
            self.cur_chat_lbl.configure(text="")
            self.clear_textbox()


    def open_chat(self, username):
        if self.master.current_chat == username:
            return

        self.master.current_chat = username
        self.cur_chat_lbl.configure(text=username)
        self.clear_textbox()
        history = self.master.get_message_history(username)
        self.textbox.configure(state="normal")
        for row in history:
            self.textbox.insert("end", f"{row[0]}: {row[2]}\n")
        self.textbox.configure(state="disabled")
        self.textbox.yview("end")


    def send_message_wrapper(self, event):
        content = self.msg_entry.get()
        self.msg_entry.delete("0", "end")
        if content and self.master.current_chat:
            self.master.send_message(content)


    def display_friends_buttons(self):
        friends = self.master.request_friends_list()
        for friend in friends:
            self.master.friends_list.append(friend)
            self.create_full_friend_button(friend)


class LoginFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.name = "LoginFrame"

        frame_width = 350
        frame_height = 400
        widgets_width = 250
        widgets_height = 25

        self.login_frame = CTkFrame(master=self, width=frame_width, height=frame_height)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="c")
        self.login_frame.pack_propagate(False)

        logo = CTkImage(dark_image=Image.open("assets/triorb.png"), size=(150, 150))

        self.lbl_image = CTkLabel(master=self.login_frame, text="", image=logo, width=150, height=150)
        self.lbl_image.pack(pady=2.5)

        self.entry_username = CTkEntry(master=self.login_frame, width=widgets_width, height=widgets_height,
                                       placeholder_text="Введите имя пользователя")
        self.entry_username.pack(pady=2.5)

        self.entry_password = CTkEntry(master=self.login_frame, width=widgets_width, height=widgets_height,
                                       placeholder_text="Введите пароль", show="•")
        self.entry_password.pack(pady=2.5)

        self.show_pass_var = StringVar(value="hide")
        self.checkbox_show_hide_password = CTkCheckBox(master=self.login_frame,
                                                       width=widgets_width,
                                                       height=widgets_height,
                                                       text="Показать пароль",
                                                       onvalue="show",
                                                       offvalue="hide",
                                                       variable=self.show_pass_var,
                                                       command=self.show_hide_password)
        self.checkbox_show_hide_password.pack(pady=2.5)

        #self.checkbox_remember = CTkCheckBox(master=self.login_frame, width=widgets_width, height=widgets_height,
        #                                     text="Запомнить меня", checkbox_width=25, checkbox_height=25)
        #self.checkbox_remember.pack(pady=2.5)

        self.btn_submit = CTkButton(master=self.login_frame, width=widgets_width, height=widgets_height, text="Войти",
                                    command=self.login_wrapper)
        self.btn_submit.pack(pady=2.5)

        self.btn_go_to_reg = CTkButton(master=self.login_frame, width=widgets_width, height=widgets_height,
                                       text="Зарегистрироваться", command=self.master.open_register_frame)
        self.btn_go_to_reg.pack(pady=2.5)

        self.lbl_login_status = CTkLabel(master=self.login_frame, width=widgets_width, height=widgets_height, text="")
        self.lbl_login_status.pack(pady=2.5)


    def show_hide_password(self):
        if self.show_pass_var.get() == "show":
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="•")


    def login_wrapper(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if len(username) == 0 or len(password) == 0:
            self.lbl_login_status.configure(text="Введите логин и пароль", text_color="#c90808")
            return

        status = self.master.login(username, password)
        if status == "SUCCESS":
            self.master.username = username
            self.master.open_main_frame()
        elif status == "USER_DOES_NOT_EXIST":
            self.lbl_login_status.configure(text="Пользователь не найден", text_color="#c90808")
        elif status == "INCORRECT_PASSWORD":
            self.lbl_login_status.configure(text="Неверный пароль", text_color="#c90808")
        else:
            self.lbl_login_status.configure(text=f"Неизвестный статус входа: {status}", text_color="#c90808")


class RegisterFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.name = "RegisterFrame"

        frame_width = 350
        frame_height = 400
        widgets_width = 250
        widgets_height = 25

        self.register_frame = CTkFrame(master=self, width=frame_width, height=frame_height)
        self.register_frame.place(relx=0.5, rely=0.5, anchor="c")
        self.register_frame.pack_propagate(False)

        logo = CTkImage(dark_image=Image.open("assets/triorb.png"), size=(150, 150))

        self.lbl_image = CTkLabel(master=self.register_frame, text="", image=logo, width=150, height=150)
        self.lbl_image.pack(pady=2.5)

        self.entry_username = CTkEntry(master=self.register_frame, width=widgets_width, height=widgets_height,
                                       placeholder_text="Выберите имя пользователя")
        self.entry_username.pack(pady=2.5)

        self.entry_password1 = CTkEntry(master=self.register_frame, width=widgets_width, height=widgets_height,
                                        placeholder_text="Выберите пароль", show="•")
        self.entry_password1.pack(pady=2.5)

        self.entry_password2 = CTkEntry(master=self.register_frame, width=widgets_width, height=widgets_height,
                                        placeholder_text="Введите пароль ещё раз", show="•")
        self.entry_password2.pack(pady=2.5)

        self.show_pass_var = StringVar(value="hide")
        self.checkbox_show_hide_password = CTkCheckBox(master=self.register_frame,
                                                       width=widgets_width,
                                                       height=widgets_height,
                                                       text="Показать пароль",
                                                       onvalue="show",
                                                       offvalue="hide",
                                                       variable=self.show_pass_var,
                                                       command=self.show_hide_password)
        self.checkbox_show_hide_password.pack(pady=2.5)

        self.checkbox_remember = CTkCheckBox(master=self.register_frame, width=widgets_width, height=widgets_height,
                                             text="Запомнить меня", checkbox_width=25, checkbox_height=25)
        # self.checkbox_remember.pack(pady=2.5)

        self.btn_submit = CTkButton(master=self.register_frame, width=widgets_width, height=widgets_height,
                                    text="Войти", command=self.master.open_login_frame)
        self.btn_submit.pack(pady=2.5)

        self.btn_go_to_reg = CTkButton(master=self.register_frame, width=widgets_width, height=widgets_height,
                                       text="Зарегистрироваться", command=self.register_wrapper)
        self.btn_go_to_reg.pack(pady=2.5)

        self.lbl_register_status = CTkLabel(master=self.register_frame, width=widgets_width, height=widgets_height,
                                            text="")
        self.lbl_register_status.pack(pady=2.5)


    def show_hide_password(self):
        if self.show_pass_var.get() == "show":
            self.entry_password1.configure(show="")
            self.entry_password2.configure(show="")
        else:
            self.entry_password1.configure(show="•")
            self.entry_password2.configure(show="•")


    def register_wrapper(self):
        username = self.entry_username.get()
        password1 = self.entry_password1.get()
        password2 = self.entry_password2.get()

        if len(username) <= 5:
            self.lbl_register_status.configure(text="Имя пользователя должно состоять\n не менее чем из 5 символов", text_color="#c90808")
            return
        if len(username) > 20:
            self.lbl_register_status.configure(text="Длина имени пользователя не\n должна превышать 20 символов", text_color="#c90808")
            return
        if len(password1) <= 8:
            self.lbl_register_status.configure(text="Пароль должен состоять\n не менее чем из 8 символов", text_color="#c90808")
            return
        if len(password1) > 50:
            self.lbl_register_status.configure(text="Длина пароля не должна\n превышать 50 символов", text_color="#c90808")
            return
        if password1 != password2:
            self.lbl_register_status.configure(text="Пароли не совпадают", text_color="#c90808")
            return

        status = self.master.sign_up(username, password1)

        if status == "SUCCESS":
            self.master.username = username
            self.master.open_main_frame()
        elif status == "USERNAME_IS_ALREADY_TAKEN":
            self.lbl_register_status.configure(text="Имя пользователя занято", text_color="#c90808")
            return
        else:
            self.lbl_register_status.configure(text=f"Неизвестный статус регистрации: {status}", text_color="#c90808")


class SettingsFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.name = "SettingsFrame"

        self.settings_frame = CTkFrame(master=self, width=350, height=350)
        self.settings_frame.place(relx=0.5, rely=0.5, anchor="c")
        self.settings_frame.pack_propagate(False)

        self.return_btn = CTkButton(master=self, text="Вернуться", command=self.master.open_main_frame)
        self.return_btn.place(x=5, y=5)

        self.delete_account_btn = CTkButton(master=self.settings_frame, text="Удалить аккаунт", command=self.delete_account)
        self.delete_account_btn.pack(padx=2.5, pady=2.5, fill="x", side="bottom")

    def delete_account(self):
        self.master.request_account_deletion()
        self.master.logout()

