from random import randint
from datetime import datetime
import sqlite3


class Database:
    def __init__(self, db_name='main.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
                        name TEXT,
                        identifier TEXT,
                        bankNumber TEXT,
                        phoneNumber TEXT,
                        password TEXT,
                        cardNumber TEXT
                    )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS accounts (
                        bankNumber TEXT,
                        cardNumber TEXT,
                        demand_balance INTEGER,
                        fixed_balance INTEGER,
                        createDate TEXT,
                        freeze TEXT
                    )""")
        self.conn.commit()

    def write_info(self, name, identifier, phoneNumber, password):
        try:
            cur = self.cur
            conn = self.conn

            cur.execute("SELECT cardNumber FROM users")
            numbers = cur.fetchall()

            cardNumber = ' '.join([str(randint(1000, 9999)) for _ in range(4)])
            while cardNumber in numbers:
                cardNumber = ' '.join([str(randint(1000, 9999)) for _ in range(4)])

            bankNumber = ''.join([str(randint(100, 999)) for _ in range(3)])
            while bankNumber in numbers:
                bankNumber = ''.join([str(randint(100, 999)) for _ in range(3)])

            curDate = datetime.today().strftime("%M %Y")

            cur.execute(
                "INSERT INTO users (name, identifier, bankNumber, phoneNumber, password, cardNumber) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, identifier, bankNumber, phoneNumber, password, cardNumber))
            cur.execute("INSERT INTO accounts (bankNumber, cardNumber, demand_balance, fixed_balance, createDate, freeze) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (bankNumber, cardNumber, 0, 0, curDate, "Разблокирована"))
            conn.commit()
            return 'done'
        except sqlite3.Error as e:
            print('Ошибка при записи в базу данных:', e)
            return 'Ошибка'
