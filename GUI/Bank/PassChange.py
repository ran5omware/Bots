import tkinter as tk
from tkinter import messagebox
from OpenAccount import Database


class PasswordChange:
    def __init__(self, window):
        db = Database()
        self.cur = db.cur
        self.conn = db.conn

        self.window = window

        self.text = tk.Label(self.window, text='Нужно удостовериться, что это действительно вы', font=('Ariel bold', 9))
        self.text.place(x=65, y=25)

        self.iden = tk.Label(self.window, text='Введите идентификатор')
        self.iden.place(x=150, y=55)
        self.EnterId = tk.Entry(self.window, width=30)
        self.EnterId.place(x=95, y=85)

        self.pn = tk.Label(self.window, text='Введите номер телефона')
        self.pn.place(x=140, y=115)
        self.EnterPN = tk.Entry(self.window, width=30)
        self.EnterPN.place(x=95, y=145)

        self.cn = tk.Label(self.window, text='Введите номер карты')
        self.cn.place(x=140, y=175)
        self.EnterCN = tk.Entry(self.window, width=30)
        self.EnterCN.place(x=95, y=205)

        conf = tk.Button(self.window, text='Проверить', command=self.change, width=20, height=1)
        conf.place(x=130, y=265)

    def change(self):
        identifier = self.EnterId.get()
        cardNumber = self.EnterCN.get()
        phoneNumber = self.EnterPN.get()
        self.cur.execute("SELECT identifier, cardNumber, phoneNumber FROM users WHERE identifier=?", (identifier,))
        result = self.cur.fetchone()
        if result is None:
            messagebox.showinfo('Ошибка',
                                'Ошибка, пользователь с таким набором параметров не найден, попробуйте еще раз')
        elif result[1] != cardNumber or result[2] != phoneNumber:
            messagebox.showinfo('Ошибка',
                                'Ошибка, пользователь с таким набором параметров не найден, попробуйте еще раз')
        else:
            self.window.destroy()
            changeWindow = tk.Tk()

            changeWindow.title('Смена пароля')
            changeWindow.geometry('400x300')
            changeWindow.resizable(width=False, height=False)

            newPass = tk.Label(changeWindow, text='Введите новый пароль')
            newPass.place(x=150, y=25)
            EnterNewPass = tk.Entry(changeWindow, width=40)
            EnterNewPass.place(x=85, y=55)

            conf = tk.Button(changeWindow, text='Сохранить', command=lambda: self.save_pass(identifier, EnterNewPass.get(), changeWindow), width=20, height=1)
            conf.place(x=130, y=115)

            changeWindow.mainloop()
        return 'done'

    def save_pass(self, identifier, password, window):
        self.cur.execute("UPDATE users SET password=? WHERE identifier=?", (password, identifier))
        self.conn.commit()
        messagebox.showinfo(message='Успешно сохранено')
        window.destroy()
        return 'done'
