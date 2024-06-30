from tkinter import messagebox
from OpenAccount import Database


class Lock:
    def __init__(self):

        messagebox.showinfo(message='Ваша учетная запись была заблокирована')

        db = Database()
        self.cur = db.cur
        self.conn = db.conn

    def lock(self, bankNumber):
        self.cur.execute("UPDATE accounts SET freeze=? WHERE bankNumber=?", ('Заблокирована', bankNumber))
        self.conn.commit()
        return 'done'
