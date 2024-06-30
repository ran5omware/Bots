import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database
from Lock import Lock
from random import randint


class Transfer:
    def __init__(self, window, bankNumber):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn

        self.passCount = 0
        self.curBal = 0

        self.bankNumber = bankNumber
        self.window = window

        self.text = tk.Label(self.window, text='Перевод', font=('Ariel bold', 12))
        self.text.place(x=140, y=25)

        self.cash = tk.Label(self.window, text='Введите сумму:')
        self.cash.place(x=20, y=75)
        self.EnterCash = tk.Entry(self.window, width=20)
        self.EnterCash.place(x=220, y=75)

        self.card = tk.Label(self.window, text='Введите карту назначения:')
        self.card.place(x=20, y=125)
        self.EnterCard = tk.Entry(self.window, width=20)
        self.EnterCard.place(x=220, y=125)

        self.password = tk.Label(self.window, text='Введите ваш пароль')
        self.password.place(x=120, y=175)
        self.EnterPass = tk.Entry(self.window, width=30)
        self.EnterPass.place(x=80, y=205)

        conf = tk.Button(self.window, text='Перевести', command=self.withdraw, width=20, height=1)
        conf.place(x=130, y=255)

    def withdraw(self):
        if self.passCount == 3:
            l = Lock()
            l.lock(self.bankNumber)
            self.window.destroy()
        self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        if self.cur.fetchone()[0] >= int(self.EnterCash.get()):
            self.cur.execute("SELECT password FROM users WHERE bankNumber=?", (self.bankNumber,))
            if self.cur.fetchone()[0] == self.EnterPass.get():
                self.cur.execute("SELECT bankNumber FROM users WHERE cardNumber=?", (self.EnterCard.get(),))
                if self.cur.fetchone():
                    self.cur.execute("SELECT bankNumber FROM users WHERE cardNumber=?", (self.EnterCard.get(),))
                    bankNumber = self.cur.fetchone()[0]
                    self.cur.execute("UPDATE accounts SET demand_balance=? WHERE bankNumber=?", (self.EnterCash.get(), bankNumber))
                    self.conn.commit()
                    self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
                    self.curBal = self.cur.fetchone()[0]
                    details = f"Информация по переводу\n" \
                              f"Чек номер {randint(1_000_000, 9_999_999)}\n" \
                              f"Ваш текущий баланс: {self.curBal}"
                    tk.messagebox.showinfo("Ваучер снятия", details)
                    self.window.destroy()
                else:
                    tk.messagebox.showinfo('Ошибка', 'Указанная карта не найдена')
            else:
                self.passCount += 1
                tk.messagebox.showinfo('Ошибка', f'Вы ввели неверный пароль, осталось попыток: {3 - self.passCount}')
        else:
            tk.messagebox.showinfo('Ошибка', 'У вас нет столько средств')
