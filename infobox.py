from customtkinter import *


class InfoBox(CTkToplevel):
    def __init__(self, master, width : int = 400, height : int = 200, title : str = "CTkMessageBox", text : str = "Message"):
        super().__init__()
        self.master : CTk = master

        self.width = width
        self.height = height
        self.text = text

        self.selected_option = False

        spawn_x = (self.winfo_screenwidth() - width) // 2
        spawn_y = (self.winfo_screenheight() - height) // 2

        self.geometry(f"{width}x{height}+{spawn_x}+{spawn_y}")
        self.resizable(False, False)
        self.title(title)
        self.lift()
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.create_widgets)
        self.grab_set()


    def create_widgets(self):
        self.info_lbl = CTkLabel(master=self, text=self.text, font=("Ariel", 20))
        self.info_lbl.pack(fill="both", expand=True)

        self.ok_btn = CTkButton(master=self, text="ОК", height=50, command=self.ok_event)
        self.ok_btn.pack(side="bottom", fill="x")

    def ok_event(self):
        self.grab_release()
        self.destroy()

    def on_closing(self):
        self.grab_release()
        self.destroy()


if __name__ == "__main__":
    root = CTk()
    root.geometry("400x300+300+300")
    box = InfoBox(root, text="Такого пользователя не существует")
    root.mainloop()