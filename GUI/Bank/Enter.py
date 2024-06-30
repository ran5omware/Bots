import tkinter as tk
from tkinter import messagebox
from MainWindow import Window
from Lock import Lock
from OpenAccount import Database
from registration import Registration


class Enter:

    def __init__(self):
        self.window = tk.Tk()

        self.window.resizable(width=False, height=False)
        self.window.title('Вход')
        self.window.geometry('400x350')
        self.count = 0

        self.iden = tk.Label(self.window, text='Введите идентификатор')
        self.iden.place(x=120, y=25)
        self.EnterId = tk.Entry(self.window, width=30)
        self.EnterId.place(x=85, y=55)

        self.password = tk.Label(self.window, text='Введите пароль')
        self.password.place(x=140, y=85)
        self.EnterPass = tk.Entry(self.window, width=30)
        self.EnterPass.place(x=85, y=115)

        conf = tk.Button(self.window, text='Войти', command=self.log, width=20, height=1)
        conf.place(x=120, y=245)
        reg = tk.Button(self.window, text='Зарегистрироваться', command=self.registration, width=20, height=1)
        reg.place(x=120, y=285)

        self.window.mainloop()

    def log(self):
        identifier = self.EnterId.get()
        password = self.EnterPass.get()
        if identifier == '' or password == '':
            tk.messagebox.showinfo("Ошибка", "Пустое поле")
        else:
            db = Database()
            db.cur.execute("SELECT bankNumber, identifier, password FROM users WHERE identifier=?", (identifier,))
            result = db.cur.fetchone()
            if result:
                bankNumber = result[0]
                self.count += 1
                if self.count == 3:
                    b = Lock()
                    b.lock(bankNumber)
                elif result[1] == identifier and result[2] == password:
                    messagebox.showinfo("Popup", "Вы успешно вошли")
                    self.window.destroy()
                    Window(identifier)
                else:
                    messagebox.showinfo("Ошибка", "Вы ввели неверные данные, возможно вы не зарегистрированы")
            else:
                messagebox.showinfo("Ошибка", "Вы ввели неверные данные, возможно вы не зарегистрированы")

    def registration(self):
        self.window.destroy()
        Registration()
