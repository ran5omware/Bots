import tkinter as tk
from OpenAccount import Database
from Withdrawal import Withdrawal
from tkinter import messagebox


class Cancel:
    def __init__(self, window, bankNumber):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn

        self.bankNumber = bankNumber
        self.window = window

        self.text = tk.Label(self.window, text='Удаление аккаунта',
                             font=('Ariel bold', 12))
        self.text.place(x=100, y=25)

        self.yesno = tk.Label(self.window, text='Вы уверены, что хотите удалить аккаунт? (да/нет)')
        self.yesno.place(x=30, y=85)
        self.EnterYN = tk.Entry(self.window, width=30)
        self.EnterYN.place(x=85, y=115)

        conf = tk.Button(self.window, text='Удалить аккаунт', command=self.cancel, width=20, height=1)
        conf.place(x=120, y=265)

    def cancel(self):
        self.cur.execute("SELECT demand_balance, fixed_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        DebBal, FixBal = self.cur.fetchone()
        if DebBal != 0 and FixBal != 0:
            tk.messagebox.showinfo("Ошибка удаления", "Вначале снимите все средства со своего счета")
            self.window.destroy()
        elif self.EnterYN.get().lower() == "да":
            self.cur.execute("DELETE FROM users WHERE bankNumber=?", (self.bankNumber,))
            self.cur.execute("DELETE FROM accounts WHERE bankNumber=?", (self.bankNumber,))
            self.conn.commit()
            tk.messagebox.showinfo("Успех", "Ваш аккаунт успешно удален")
            self.window.destroy()
        else:
            tk.messagebox.showinfo(message="Ваш аккаунт не был удален")
            self.window.destroy()


