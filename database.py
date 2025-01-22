import sqlite3
from datetime import datetime
from typing import List, Tuple


class Database:
    def __init__(self, name : str) -> None:
        self.connection = sqlite3.connect(name + ".db")
        self.cursor = self.connection.cursor()
        self.create_tables()


    def create_tables(self) -> None:
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender VARCHAR(100) NOT NULL,
        receiver VARCHAR(100) NOT NULL,
        text TEXT NOT NULL,
        sent_at CHAR(20) NOT NULL
        )
        ''')

        self.connection.commit()


    def add_user(self, username: str, password: str) -> None:
        self.cursor.execute('''
        INSERT INTO Users (username, password) VALUES (?, ?)
        ''', (username, password))

        self.connection.commit()


    def delete_user(self, username: str) -> None:
        self.cursor.execute('''
        DELETE FROM Users
        WHERE username = ?
        ''', (username,))

        self.cursor.execute('''
        DELETE FROM Messages
        WHERE sender = ? OR receiver = ?
        ''', (username, username))

        self.connection.commit()


    def add_message(self, sender: str, receiver: str, text: str) -> None:
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('''
        INSERT INTO Messages (sender, receiver, text, sent_at) VALUES (?, ?, ?, ?)
        ''', (sender, receiver, text, cur_time))

        self.connection.commit()


    def load_message_history(self, username1 : str, username2 : str) -> List[Tuple[str, str, str, str]]:
        self.cursor.execute('''
        SELECT * FROM Messages
        WHERE sender = ? AND receiver = ? OR sender = ? AND receiver = ?
        ORDER BY sent_at ASC
        ''', (username1, username2, username2, username1))
        history = self.cursor.fetchall()
        history = [message[1:] for message in history]  # Удаление id сообщений из результирующего массива
        return history


    def delete_message_history(self, username1 : str, username2 : str) -> None:
        self.cursor.execute('''
                DELETE FROM Messages
                WHERE sender = ? AND receiver = ? OR sender = ? AND receiver = ?
                ''', (username1, username2, username2, username1))

        self.connection.commit()


    def get_user_password(self, username : str) -> str:
        self.cursor.execute('''
        SELECT password FROM Users
        WHERE username = ?
        ''', (username, ))
        return self.cursor.fetchone()[0]


    def check_if_user_exists(self, username : str) -> bool:
        self.cursor.execute('''
        SELECT * FROM Users WHERE username = ?
        ''', (username,))
        return self.cursor.fetchall() != []


    def delete_all_data(self) -> None:
        self.cursor.execute("DELETE FROM Users")
        self.cursor.execute("DELETE FROM Messages")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='Users';")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='Messages';")
        self.connection.commit()


    def show_tables(self) -> None:
        print("--------Users--------")
        self.cursor.execute('''
        SELECT * FROM Users
        ''')
        for row in self.cursor.fetchall():
            print(row)

        print("--------Messages--------")
        self.cursor.execute('''
        SELECT * FROM Messages
        ''')
        for row in self.cursor.fetchall():
            print(row)


    def close_connection(self) -> None:
        self.connection.close()


if __name__ == "__main__":
    db = Database("Raziel")
    db.show_tables()