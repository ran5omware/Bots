import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database
from Lock import Lock
from random import randint
from datetime import datetime


class Withdrawal:
    def __init__(self, window, bankNumber):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn

        self.passCount = 0
        self.curBal = 0

        self.bankNumber = bankNumber
        self.window = window

        self.text = tk.Label(self.window, text='Снятие', font=('Ariel bold', 12))
        self.text.place(x=140, y=25)

        self.cash = tk.Label(self.window, text='Введите сумму:')
        self.cash.place(x=20, y=75)
        self.EnterCash = tk.Entry(self.window, width=20)
        self.EnterCash.place(x=220, y=75)

        self.password = tk.Label(self.window, text='Введите пароль:')
        self.password.place(x=20, y=125)
        self.EnterPass = tk.Entry(self.window, width=20)
        self.EnterPass.place(x=220, y=125)

        conf = tk.Button(self.window, text='Вывести с фиксированного счета', command=self.withdrawal_fix, width=30, height=1)
        conf.place(x=80, y=255)

        conf = tk.Button(self.window, text='Вывести с дебетового счета', command=self.withdrawal_deb, width=30, height=1)
        conf.place(x=80, y=215)

    def withdrawal_deb(self):
        if self.passCount == 3:
            l = Lock()
            l.lock(self.bankNumber)
            self.window.destroy()
        self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        if self.cur.fetchone()[0] >= int(self.EnterCash.get()):
            self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
            self.curBal = self.cur.fetchone()[0] - int(self.EnterCash.get())
            self.cur.execute("SELECT password FROM users WHERE bankNumber=?", (self.bankNumber,))
            if self.cur.fetchone()[0] == self.EnterPass.get():

                details = f"Информация по снятию\n" \
                          f"Чек номер {randint(1_000_000, 9_999_999)}\n" \
                          f"Ваш текущий баланс: {self.curBal}"
                tk.messagebox.showinfo("Ваучер снятия", details)
                self.cur.execute("UPDATE accounts SET demand_balance=? WHERE bankNumber=?",
                                (self.curBal, self.bankNumber))
                self.conn.commit()
                self.window.destroy()

            else:
                self.passCount += 1
                tk.messagebox.showinfo('Ошибка', f'Вы ввели неверный пароль, осталось попыток: {3 - self.passCount}')
        else:
            tk.messagebox.showinfo('Ошибка', 'У вас нет столько средств')

    def withdrawal_fix(self):
        if self.passCount == 3:
            l = Lock()
            l.lock(self.bankNumber)
            self.window.destroy()
        self.cur.execute("SELECT fixed_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        if self.cur.fetchone()[0] >= int(self.EnterCash.get()):
            self.cur.execute("SELECT fixed_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
            self.curBal = self.cur.fetchone()[0] - int(self.EnterCash.get())
            self.cur.execute("SELECT password FROM users WHERE bankNumber=?", (self.bankNumber,))
            if self.cur.fetchone()[0] == self.EnterPass.get():
                self.cur.execute("SELECT createDate FROM accounts WHERE bankNumber=?", (self.bankNumber,))
                regDate = self.cur.fetchone()[0]
                nowDay = datetime.today().strftime("%M %Y")

                if int(regDate[-1]) == int(nowDay[-1]) - 1:
                    details = f"Информация по снятию\n" \
                              f"Чек номер {randint(1_000_000, 9_999_999)}\n" \
                              f"Ваш текущий баланс: {self.curBal}"
                    tk.messagebox.showinfo("Ваучер снятия", details)
                    self.cur.execute("UPDATE accounts SET fixed_balance=? WHERE bankNumber=?", (self.curBal, self.bankNumber))
                    self.conn.commit()
                    self.window.destroy()
                else:
                    tk.messagebox.showinfo("Ошибка", 'Вывод еще не доступен')

            else:
                tk.messagebox.showinfo('Ошибка', f'Вы ввели неверный пароль, осталось попыток: {3 - self.passCount}')
                self.passCount += 1
        else:
            tk.messagebox.showinfo('Ошибка', 'У вас нет столько средств')
