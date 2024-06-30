import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database


class Unlock:
    def __init__(self, window):
        self.window = window
        self.count = 0

        self.iden = tk.Label(self.window, text='Введите идентификатор')
        self.iden.place(x=140, y=25)
        self.EnterId = tk.Entry(self.window, width=30)
        self.EnterId.place(x=95, y=55)

        self.bN = tk.Label(self.window, text='Введите номер банковского счета')
        self.bN.place(x=110, y=85)
        self.EnterBN = tk.Entry(self.window, width=30)
        self.EnterBN.place(x=95, y=115)

        self.password = tk.Label(self.window, text='Введите пароль')
        self.password.place(x=140, y=145)
        self.EnterPass = tk.Entry(self.window, width=30)
        self.EnterPass.place(x=95, y=175)

        conf = tk.Button(self.window, text='Разблокировать', command=self.unlock, width=20, height=1)
        conf.place(x=130, y=245)

        db = Database()
        self.cur = db.cur
        self.conn = db.conn

    def unlock(self):
        if self.count == 3:
            messagebox.showinfo(message='Превышено количество попыток ввода пароля')
            self.window.destroy()
        else:
            bankNumber = self.EnterBN.get()
            identifier = self.EnterId.get()
            password = self.EnterPass.get()
            try:
                self.cur.execute("SELECT identifier, password FROM users WHERE bankNumber=?", (bankNumber,))
                result = self.cur.fetchone()
                if result[0] == identifier and result[1] == password:
                    self.cur.execute("UPDATE accounts SET freeze=? WHERE bankNumber=?", ('Разблокирована', bankNumber))
                    self.conn.commit()
                    messagebox.showinfo(message='Ваша учетная запись успешно разблокирована')
                    self.window.destroy()
                else:
                    self.count += 1
                    messagebox.showinfo(message=f'Данные введены неверно, попробуйте еще раз, осталось попыток: {3 - self.count}')
                return 'done'
            except Exception as e:
                print(e)
                self.count += 1
