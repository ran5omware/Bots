import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database


class Deposit:
    def __init__(self, window, bankNumber):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn
        self.bankNumber = bankNumber

        self.window = window

        self.text = tk.Label(self.window, text='Укажите сумму', font=('Ariel bold', 12))
        self.text.place(x=140, y=25)

        self.fix = tk.Label(self.window, text='На фиксированный счет:')
        self.fix.place(x=20, y=75)
        self.EnterFix = tk.Entry(self.window, width=20)
        self.EnterFix.place(x=220, y=75)

        self.dem = tk.Label(self.window, text='На дебетовый счет:')
        self.dem.place(x=20, y=125)
        self.EnterDem = tk.Entry(self.window, width=20)
        self.EnterDem.place(x=220, y=125)

        conf = tk.Button(self.window, text='Пополнить', command=self.top_up, width=20, height=1)
        conf.place(x=130, y=255)

    def top_up(self):
        self.cur.execute("SELECT fixed_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        fixed_balance = self.cur.fetchone()[0]

        self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        demand_balance = self.cur.fetchone()[0]
        self.cur.execute("UPDATE accounts SET demand_balance=? WHERE bankNumber=?", (demand_balance + int(self.EnterDem.get()), self.bankNumber))
        self.cur.execute("UPDATE accounts SET fixed_balance=? WHERE bankNumber=?", (fixed_balance + int(self.EnterFix.get()), self.bankNumber))
        self.conn.commit()

        self.cur.execute("SELECT fixed_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        fixed_balance = self.cur.fetchone()[0]

        self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (self.bankNumber,))
        demand_balance = self.cur.fetchone()[0]
        details = f"Информация по аккаунту\n" \
                  f"Сумма фиксированного депозита: {fixed_balance}\n" \
                  f"Процентная ставка: 15%\n" \
                  f"Сумма депозита до востребования: {demand_balance}\n" \
                  f"Процентная ставка: 3%\n"
        tk.messagebox.showinfo("Депозитный ваучер", details)
        self.window.destroy()
