import sqlite3
from os import remove

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    position TEXT NOT NULL,
    department TEXT NOT NULL,
    chief_id INTEGER
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Clients (
    id_client INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone_number TEXT,
    passport TEXT
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    CPU TEXT,
    GPU TEXT,
    Motherboard TEXT,
    RAM TEXT,
    "Case" TEXT,
    available BOOLEAN,
    client_id INTEGER,
    price INTEGER
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Contracts (
    id_contract INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    date TEXT,
    deal_type TEXT,
    start_price INTEGER,
    discount INTEGER,
    deal_status TEXT,
    finall_price INTEGER,
    id INTEGER,
    client_id INTEGER,
    employee_id INTEGER
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Reports (
    id_report INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    date TEXT,
    report_type TEXT,
    description TEXT,
    employee_id INTEGER
)""")

cursor.execute('INSERT INTO Employees (name, email, phone_number, position, department, chief_id) VALUES (?, ?, ?, ?, ?, ?)',
               ("Агатов Н.Р.", "agatov@gmail.com", "+7964323321", "Менеджер", "Хозяйственный Отдел", 2))

cursor.execute("INSERT INTO Clients (name, email, phone_number, passport) VALUES (?, ?, ?, ?)",
               ("Контрагент Нулл", "couNull@null.com", "+70001001010", "4500 234900"))

cursor.execute("INSERT INTO Computers (id, CPU, GPU, Motherboard, RAM, \"Case\", available, client_id, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (0, "Ryzen 5 7600x", "Palit rtx 4060ti dual OC", "Asrock A620M-H", "ADATA XPG Lancer DDR5 5600MHz", "ARDOR GAMING Rare M6", False, 5, 1299999))

cursor.execute("INSERT INTO Contracts (id_contract, number, date, deal_type, start_price, discount, deal_status, finall_price, id, client_id, employee_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (0, "1234", "28.12.2024", "rent", 129999, 5000, "complete", 124000, 0, 5, 0))

cursor.execute("INSERT INTO Reports (number, date, report_type, description, employee_id) VALUES (?, ?, ?, ?, ?)",
               ("145", "28.04.2024", "", "", 0))

conn.commit()
conn.close()
