import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database


class Balance:
    def __init__(self, window, bankNumber):
        db = Database()
        self.cur = db.cur

        self.window = window

        self.cur.execute("SELECT freeze FROM accounts WHERE bankNumber=?",(bankNumber,))

        freeze = self.cur.fetchone()[0]

        if freeze == "Заблокирована":
            self.text = tk.Label(self.window, text='Ваш аккаунт заблокирован.',
                                 font=('Ariel bold', 16))
            self.text.place(x=75, y=65)
            self.text = tk.Label(self.window, text='Сначала разблокируйте его.',
                                 font=('Ariel bold', 12))
            self.text.place(x=75, y=95)
        else:
            self.text = tk.Label(self.window, text='Номер карты:',
                                 font=('Ariel bold', 12))
            self.text.place(x=25, y=25)
            self.cur.execute("SELECT cardNumber FROM accounts WHERE bankNumber=?", (bankNumber,))
            cardNumber = self.cur.fetchone()[0]
            self.text = tk.Label(self.window, text=cardNumber,
                                 font=('Ariel bold', 12))

            self.text.place(x=145, y=25)
            self.text = tk.Label(self.window, text='Дебетовый баланс:',
                                 font=('Ariel bold', 12))
            self.text.place(x=25, y=75)
            self.cur.execute("SELECT demand_balance FROM accounts WHERE bankNumber=?", (bankNumber,))
            self.demand_balance = str(self.cur.fetchone()[0]) + " руб."
            self.text = tk.Label(self.window, text=self.demand_balance,
                                 font=('Ariel bold', 12))
            self.text.place(x=185, y=75)

            self.text = tk.Label(self.window, text='Баланс вложений:',
                                 font=('Ariel bold', 12))
            self.text.place(x=25, y=125)
            self.cur.execute("SELECT fixed_balance FROM accounts WHERE bankNumber=?", (bankNumber,))
            self.fixed_balance = str(self.cur.fetchone()[0]) + " руб."
            self.text = tk.Label(self.window, text=self.fixed_balance,
                                 font=('Ariel bold', 12))
            self.text.place(x=185, y=125)

            conf = tk.Button(self.window, text='Распечатать', command=self.print, width=20, height=1)
            conf.place(x=130, y=255)

    def print(self):
        details = f"Информация по аккаунту\n" \
                  f"Баланс фиксированного депозита: {self.fixed_balance}\n" \
                  f"Процентная ставка: 15%\n" \
                  f"Баланс депозита до востребования: {self.demand_balance}\n" \
                  f"Процентная ставка: 3%\n"
        tk.messagebox.showinfo("Баланс", details)
        self.window.destroy()
