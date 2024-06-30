import sqlite3
import tkinter as tk
from Lock import Lock
from random import randint
from tkinter import messagebox
from OpenAccount import Database


class CardChange:
    def __init__(self, window):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn

        self.window = window
        self.count = 0

        self.text = tk.Label(self.window, text='Нужно удостовериться, что это действительно вы', font=('Ariel bold', 9))
        self.text.place(x=65, y=25)

        self.iden = tk.Label(self.window, text='Введите идентификатор')
        self.iden.place(x=150, y=55)
        self.EnterId = tk.Entry(self.window, width=30)
        self.EnterId.place(x=95, y=85)

        self.password = tk.Label(self.window, text='Введите пароль')
        self.password.place(x=140, y=115)
        self.EnterPass = tk.Entry(self.window, width=30)
        self.EnterPass.place(x=95, y=145)

        conf = tk.Button(self.window, text='Выпустить новую карту', command=self.change, width=20, height=1)
        conf.place(x=130, y=265)

    def change(self):
        identifier = self.EnterId.get()
        password = self.EnterPass.get()
        self.cur.execute("SELECT bankNumber FROM users WHERE identifier=?", (identifier,))
        bankNumber = self.cur.fetchone()[0]
        self.cur.execute("SELECT freeze FROM accounts WHERE bankNumber=?", (bankNumber,))
        if self.cur.fetchone()[0] == 'Заблокирована':
            messagebox.showinfo('Ошибка', 'Ваша карта заблокирована, вы не можете ее поменять, пока не разблокируете')
            self.window.destroy()
        else:
            self.cur.execute("SELECT identifier, password FROM users WHERE identifier=?", (identifier,))
            result = self.cur.fetchone()
            if self.count == 3:
                self.cur.execute("SELECT bankNumber FROM users WHERE identifier=?", (identifier,))
                bankNumber = self.cur.fetchone()[0]
                l = Lock()
                l.lock(bankNumber)
            if result is None:
                self.window.withdraw()
                messagebox.showinfo('Ошибка',
                                    'Ошибка, пользователь с таким набором параметров не найден, попробуйте еще раз\n'
                                    f'Осталось {3 - self.count} попыток')
                self.count += 1
                self.window.deiconify()
            elif result[1] != password:
                self.window.withdraw()
                messagebox.showinfo('Ошибка',
                                    'Ошибка, пользователь с таким набором параметров не найден, попробуйте еще раз'
                                    f'Осталось {3 - self.count} попыток')
                self.count += 1
                self.window.deiconify()
            else:
                self.cur.execute("SELECT bankNumber FROM users WHERE identifier=?", (identifier,))
                bankNumber = self.cur.fetchone()[0]
                self.cur.execute("SELECT cardNumber FROM users")
                numbers = self.cur.fetchall()
                cardNumber = ' '.join([str(randint(1000, 9999)) for _ in range(4)])
                while cardNumber in numbers:
                    cardNumber = ' '.join([str(randint(1000, 9999)) for _ in range(4)])
                self.save_card(bankNumber, cardNumber, self.window)
            return 'done'

    def save_card(self, bankNumber, cardNumber, window):
        try:
            self.cur.execute("UPDATE users SET cardNumber=? WHERE bankNumber=?", (cardNumber, bankNumber))
            self.cur.execute("UPDATE accounts SET cardNumber=? WHERE bankNumber=?", (cardNumber, bankNumber))
        except sqlite3.Error as e:
            print(e)
        finally:
            messagebox.showinfo(message=f'Новая карта успешно выпущена\nЕе номер: {cardNumber}')
            self.conn.commit()
            window.destroy()
        return 'done'
