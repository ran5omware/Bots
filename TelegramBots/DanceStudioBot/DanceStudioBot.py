# импортируем используемые библиотеки
from telebot import *
import os
from time import sleep
import sqlite3
import requests
import datetime
from random import randint
from dotenv import load_dotenv

# загружаем переменную окружения, создаем базы данных
# и задаем вспомогательные переменные, массивы и словари
load_dotenv()

client = telebot.TeleBot(os.getenv('TOKEN'))

ui = sqlite3.connect('userInfo.db', check_same_thread=False)
sql1 = ui.cursor()
ui.commit()

pr = sqlite3.connect('practices.db', check_same_thread=False)
sql2 = pr.cursor()
pr.commit()

helpCommand = ('/start - перезапустить бота\n'
               '/help - помощь\n'
               '/reg "ФИО, дата рождения, срок окончания абонемента"'
               ' - зарегистрироваться в системе\n'
               '/registration *занятие* *день недели*'
               ' *время* - записаться на занятие')

regHelpCommand = ('Для регистрации в системе введите:\n '
                  '/reg ФИО, '
                  'дата рождения, '
                  'дата окончания абонемента\n\n'
                  'Пример: /reg Иванов Иван Иванович 01.01.2001 20.20.2020')

signupHelp = ('Для записи на занятие введите:\n '
              '/registration название занятия, '
              'день недели, '
              'время\n\n'
              'Пример: /registration Contemporary среда 17:00-19:00'
              ' (расписание смотрите по кнопке *Расписание занятий*)')

regText = ''
tag = ''
user_id = ''
lastCongratzDay = ''
lastBirthday = ''
holidays = '23.2 8.3 9.5 31.12'
direction = 'kPop BreakDance ShowDance DjazzFunk HighHeels Contemporary'
timetables = {
    'понедельник': ['HighHeels Contemporary kPop',
                    '14:00-16:00 17:00-19:00 20:00-22:00'],
    'вторник': ['BreakDance DjazzFunk',
                '14:00-16:00 19:00-21:00'],
    'среда': ['kPop Contemporary HighHeels',
              '13:00-16:00 17:00-19:00 20:00-22:00'],
    'четверг': ['BreakDance ShowDance',
                '14:00-16:00 17:00-19:00'],
    'пятница': ['BreakDance HighHeels kPop',
                '14:00-16:00 17:00-19:00 20:00-22:00'],
    'суббота': ['ShowDance kPop DjazzFunk',
                '12:00-14:00 16:00-18:00 19:00-21:00']
}

weekdays = {
    0: 'понедельник',
    1: 'вторник',
    2: 'среда',
    3: 'четверг',
    4: 'пятница',
    5: 'суббота',
    6: 'воскресенье'
}


# Команда запуска бота
@client.message_handler(commands=['start'])
def get_text(message):
    try:  # в этом блоке мы создаем таблицы в базах данных
        sql1.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT,
            tag TEXT,
            name TEXT,
            date TEXT,
            expired TEXT
        )""")

        sql1.execute("""CREATE TABLE IF NOT EXISTS reviews (
            username TEXT,
            review TEXT
        )""")

        sql2.execute("""CREATE TABLE IF NOT EXISTS practices (
            day TEXT,
            name TEXT,
            time TEXT
        )""")

        sql2.execute("""CREATE TABLE IF NOT EXISTS registration (
            lesson TEXT,
            name TEXT,
            contact TEXT,
            time TEXT
        )""")

        ui.commit()
        pr.commit()

    except sqlite3.ProgrammingError as e:
        # тут мы выводим ошибки связанные с базами данных, если таковые есть
        print(e)

    finally:
        # в этом блоке мы создаем кнопки и заполняем таблицу с расписанием
        for day in timetables:
            name = timetables[day][0]
            time = timetables[day][1]
            if sql2.execute(f"SELECT name"
                            f" FROM practices"
                            f" WHERE name = '{name}'").fetchone() is None:
                sql2.execute(f"INSERT INTO"
                             f" practices VALUES"
                             f" ('{day}', '{name}', '{time}')")
        keyboard = types.InlineKeyboardMarkup()
        buttonHelp = types.InlineKeyboardButton(
            text="Что я могу",
            callback_data="buttonHelp")
        buttonHelpReg = types.InlineKeyboardButton(
            text="Регистрация",
            callback_data="buttonHelpReg")
        buttonsignupHelp = types.InlineKeyboardButton(
            text="Запись",
            callback_data="buttonsignupHelp")
        keyboard.add(buttonHelp, buttonHelpReg, buttonsignupHelp)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Расписание занятий")
        item2 = types.KeyboardButton("Направления")
        item3 = types.KeyboardButton("Продлить абонемент")
        item4 = types.KeyboardButton("Отзывы")
        item5 = types.KeyboardButton("Помощь")
        item6 = types.KeyboardButton("Подай милоты")
        item7 = types.KeyboardButton("Что надеть")
        markup.add(item1, item2, item3, item4, item5, item6, item7)
        client.send_message(
            message.chat.id,
            f"Привет, {message.from_user.username}",
            reply_markup=markup)
        client.send_message(
            message.chat.id,
            'Выберите что вам надо',
            reply_markup=keyboard)
        pr.commit()


# команда регистрации пользователя в системе
@client.message_handler(commands=['reg'])
def registration(message):
    text = message.text.split(' ')
    flag = True  # флаг для проверки введенных данных
    try:  # проверяем правильность введенных данных
        date1 = text[4].split('.')
        date2 = text[5].split('.')
        for i in range(len(date1)):
            if not isinstance(int(date1[i]), int):
                client.send_message(
                    message.chat.id,
                    'Дата не является числом,'
                    ' пожалуйста, зарегистрируйтесь заново'
                )

                flag = False
                break
        for i in range(len(date2)):
            if not isinstance(int(date2[i]), int):
                client.send_message(
                    message.chat.id,
                    'Дата не является числом,'
                    ' пожалуйста, зарегистрируйтесь заново'
                )

                flag = False
                break
        sql1.execute("SELECT tag FROM users WHERE tag=?",
                     (message.from_user.username,))
        if sql1.fetchone():
            # если пользователь уже зарегистрирован
            client.send_message(
                message.chat.id,
                'Вы уже зарегистрированы'
            )
        elif flag:
            # создаем кнопки для сохранения данных или для их перезаполнения
            keyboard = types.InlineKeyboardMarkup()
            correct = types.InlineKeyboardButton(
                text="Данные введены правильно",
                callback_data="correct")
            incorrect = types.InlineKeyboardButton(
                text="В данных ошибка",
                callback_data="incorrect")
            keyboard.add(correct, incorrect)
            global regText, tag, user_id
            tag = message.from_user.username
            user_id = message.from_user.id
            regText = text
            ans = (f'Проверьте введенные данные:\n\n '
                   f'Ваш тэг: {tag}\n'
                   f'Фамилия: {text[1]}\n '
                   f'Имя: {text[2]}\n '
                   f'Отчество: {text[3]}\n'
                   f'Дата рождения: {text[4]}\n'
                   f'Конец абонемента: {text[5]}\n')
            client.send_message(
                message.chat.id,
                text=ans,
                reply_markup=keyboard)
    except IndexError:
        # если забыли что-то написать, то выйдет эта ошибка
        client.send_message(
            message.chat.id,
            'Проверьте введенные данные'
            ' и зарегистрируйтесь заново\nПомощь - /help'
        )


# команда записи на занятие
@client.message_handler(commands=['registration'])
def sign_up_for_lesson(message):
    sql1.execute("SELECT tag FROM users"
                 " WHERE tag = ?",
                 (message.from_user.username,))
    if sql1.fetchone():
        lesson = message.text.split(' ')[1]
        day = message.text.split(' ')[2]
        time = message.text.split(' ')[3]
        sql2.execute("SELECT * FROM practices WHERE day=?", (day,))
        lesson_info = sql2.fetchone()
        if lesson_info:  # проверка на существование занятий в выбранный день
            sql1.execute(
                "SELECT name FROM users WHERE tag=?",
                (message.from_user.username,))
            if sql1.fetchone():  # проверка на регистрацию
                name = sql1.fetchone()[0].split(' ')[1]
                sql2.execute("INSERT INTO "
                             "registration (lesson, name, contact, time) "
                             "VALUES (?, ?, ?, ?)",
                             (
                                 lesson,
                                 name,
                                 message.from_user.username,
                                 time))
                pr.commit()
                client.send_message(
                    message.chat.id,
                    f"{name} успешно записан(а)"
                    f" на занятие по {lesson} в {time}.")
            else:
                client.send_message(
                    message.chat.id,
                    "Для начала зарегистрируйтесь. Помощь - /help")
        else:
            client.send_message(
                message.chat.id,
                f"Занятие по {lesson} в {time} в этот"
                f" день не найдено в расписании.")
    else:
        client.send_message(message.chat.id, text='Сначала зарегистрируйтесь')


# команда, чтобы оставить отзыв
@client.message_handler(commands=['review'])
def review(message):
    sql1.execute("SELECT tag FROM users"
                 " WHERE tag = ?",
                 (message.from_user.username,))
    if sql1.fetchone():
        sql1.execute("SELECT username FROM reviews"
                     " WHERE username = ?",
                     (message.from_user.username,))
        if not sql1.fetchone():
            # если отзыв от этого пользователя не найдет
            # то будет выполняться код
            NewReview = message.text.replace('/review', '').strip()
            sql1.execute(f"INSERT INTO reviews VALUES "
                         f"('{message.from_user.username}', '{NewReview}')")
            client.send_message(message.chat.id, text='Спасибо за ваш отзыв!')
            ui.commit()
        else:
            client.send_message(message.chat.id, text='Вы уже оставляли отзыв')
    else:
        client.send_message(message.chat.id, text='Сначала зарегистрируйтесь')


# приемник(хэндлер) всех сообщений
@client.message_handler(content_types=['text'])
def message_reply(message):

    # если пользователь написал "помощь"
    # то выводим сообщение с кнопками для помощи
    if (message.text.lower() == "помощь"
            or message.text.lower() == "/help"
            or message.text.lower == "help"):
        keyboard = types.InlineKeyboardMarkup()
        buttonHelp = types.InlineKeyboardButton(
            text="Что я могу",
            callback_data="buttonHelp")
        buttonHelpReg = types.InlineKeyboardButton(
            text="Помощь по регистрации",
            callback_data="buttonHelpReg")
        buttonsignupHelp = types.InlineKeyboardButton(
            text="Запись",
            callback_data="buttonsignupHelp")
        keyboard.add(buttonHelp, buttonHelpReg, buttonsignupHelp)
        client.send_message(
            message.chat.id,
            "Помощь",
            reply_markup=keyboard)

    # если пользователь написал "подай милоты", то выводим гифку
    if (message.text.lower() == 'подай милоты'
            or message.text.lower() == 'подай няшности'):
        link = ('http://api.giphy.com/v1/gifs/random?'
                'api_key=LubiGqKwPL8626h5cz64oHs1QhFLrgV5&tag=cute%20kitten')
        response = requests.get(link)
        data = response.json()
        gif = data['data']['images']['original']['url']
        client.send_document(message.chat.id, gif)

    # проверка на день рождения пользователя
    # чтобы поздравить и предоставить скидку в случае дня рождения
    sql1.execute("SELECT tag FROM users"
                 " WHERE tag = ?",
                 (message.from_user.username,))
    if sql1.fetchone():
        sql1.execute("SELECT date FROM users WHERE tag = ?",
                     (message.from_user.username,))
        day = sql1.fetchone()[0].split('.')
        sendText = ('Мы рады, что вы написали нам в такой прекрасный день.\n'
                    '🎆🎆🎆Поздравляем вас с днем рождения и дарим в подарок'
                    ' скидку 20% на продление абонемента: HappyBirthday🎆🎆🎆\n\n'
                    'Покажите это сообщение администратору'
                    ' и вам предоставят скидку.')
        ddt = datetime.date.today()
        if f'{ddt.day}.{ddt.month}' == f'{int(day[0])}.{int(day[1])}':
            global lastBirthday
            if lastBirthday != ddt:
                client.send_message(message.chat.id, sendText)
                lastBirthday = ddt

    # если пользователь написал "отзыв", то присылаем ему ссылку на отзывы
    if message.text.lower() == "отзывы":
        client.send_message(
            message.chat.id,
            'https://yandex.ru/'
            'maps/org/salon_tantsev/'
            '1113579086/reviews/?ll=37.421335%2C55.887150&z=16'
        )

    # если пользователь написал "продлить абонемент"
    # то присылаем ему сообщение с кнопками для продления
    if message.text.lower() == "продлить абонемент":
        sql1.execute("SELECT tag FROM users"
                     " WHERE tag = ?",
                     (message.from_user.username,))
        if sql1.fetchone():
            keyboard = types.InlineKeyboardMarkup()
            month = types.InlineKeyboardButton(
                text="Абонемент на месяц",
                callback_data="month")
            semester = types.InlineKeyboardButton(
                text="Абонемент на полгода",
                callback_data="semester")
            year = types.InlineKeyboardButton(
                text="Абонемент на год",
                callback_data="year")
            keyboard.add(month, semester, year)
            global tag
            tag = message.from_user.username
            client.send_message(
                message.chat.id,
                text="Укажите, на какой срок вы хотите купить абонемент",
                reply_markup=keyboard
            )
        else:
            client.send_message(
                message.chat.id,
                text='Сначала зарегистрируйтесь')
    # если пользователь написал "что надеть"
    # то присылаем ему прогноз погоды
    if message.text.lower() == "что надеть" or message.text.lower() == "что надеть?":
        r = requests.get(
            f'http://api.weatherapi.com/v1/current.json?'
            f'key=61553776447e49e1b16113833241803&q=Moscow&aqi=no')
        data = r.json()
        temperature = data['current']['temp_c']
        weather = data['current']['condition']['text']
        client.send_message(
            message.chat.id,
            text=f'Погода {weather}, темература {temperature} градуса(-ов)')
    # если пользователь написал "расписание занятий"
    # то присылаем ему сообщение с кнопками для получения расписания
    if message.text.lower() == "расписание занятий":
        keyboard = types.InlineKeyboardMarkup()
        today = types.InlineKeyboardButton(
            text="На сегодня",
            callback_data="today")
        tomorrow = types.InlineKeyboardButton(
            text="На завтра",
            callback_data="tomorrow")
        keyboard.add(today, tomorrow)
        client.send_message(
            message.chat.id,
            text="Получить расписание",
            reply_markup=keyboard)

    # если пользователь написал "направления"
    # то присылаем ему все доступные направления
    if message.text.lower() == "направления":
        sendText = 'Доступные направления:\n\n'
        for names in direction.split(' '):
            sendText += f'-{names}' + '\n'
        client.send_message(message.chat.id, text=sendText)

    # проверка на праздники
    sql1.execute("SELECT id FROM users")
    values = [row[0] for row in sql1.fetchall()]
    ddt = datetime.date.today()
    if f'{ddt.day}.{ddt.month}' in holidays:
        global lastCongratzDay
        if lastCongratzDay != datetime.date.today():
            promo = randint(100000, 999999)
            sendText = ('С праздником! Можно получить скидку 15%,'
                        ' если обратиться к администратору с этим промокодом:')
            for userId in values:
                client.send_message(
                    userId,
                    f"{sendText} {promo}")
                lastCongratzDay = datetime.date.today()


# раздел бота, который принимает сигналы от инлайн-кнопок
@client.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        global tag
        global user_id
        # кнопка помощи по командам
        if call.data == "buttonHelp":
            sleep(0.3)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=helpCommand
            )

        # кнопка помощи по регистрации в системе
        if call.data == "buttonHelpReg":
            sleep(0.3)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=regHelpCommand
            )

        # кнопка помощи по записи на занятия
        if call.data == "buttonsignupHelp":
            sleep(0.3)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=signupHelp
            )

        # завершение регистрации пользователя в системе
        if call.data == "correct":
            global regText
            text = regText
            Name = f'{text[1]} {text[2]} {text[3]}'
            BirthDay = text[4]
            ExpirationDate = text[5]
            sql1.execute("SELECT tag FROM users WHERE tag = ?", (tag,))
            result = sql1.fetchone()
            if not result:
                sql1.execute(f"INSERT INTO users VALUES "
                             f"('{user_id}', '{tag}', '{Name}',"
                             f" '{BirthDay}', '{ExpirationDate}')")
                sleep(0.5)
                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text='Вы успешно зарегистрированы'
                )
                ui.commit()
            else:
                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text='Вы уже зарегистрированы'
                )

        # вывод соообщения о перерегистрации
        if call.data == 'incorrect':
            sleep(0.5)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text=f'Зарегистрируйтесь заново.'
                     f' Для помощи напишите help или помощь'
            )

        # продление абонемента на месяц
        if call.data == 'month':
            sql1.execute("SELECT expired FROM users WHERE tag = ?", (tag,))
            date1 = sql1.fetchone()
            date = date1[0].split('.')
            if int(date[1]) == 12:
                date[2] = str(int(date[2]) + 1)
                date[1] = str(1)
            else:
                date[1] = str(int(date[1]) + 1)
            if int(date[1]) < 10:
                date[1] = f'0{date[1]}'
            newDate = f'{date[0]}.{date[1]}.{date[2]}'
            sql1.execute(f"UPDATE users SET expired = ? WHERE tag = ?",
                         (newDate, tag))
            sleep(0.5)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text='Вы успешно продлили абонемент'
            )
            ui.commit()

        # продление абонемента на полгода
        if call.data == 'semester':
            sql1.execute("SELECT expired FROM users WHERE tag = ?", (tag,))
            date1 = sql1.fetchone()
            date = date1[0].split('.')
            if int(date[1]) >= 7:
                date[2] = str(int(date[2]) + 1)
                date[1] = str(int(date[1]) - 6)
            else:
                date[1] = str(int(date[1]) + 6)
            if int(date[1]) < 10:
                date[1] = f'0{date[1]}'
            newdate = f'{date[0]}.{date[1]}.{date[2]}'
            sql1.execute(f"UPDATE users SET expired = ? WHERE tag = ?",
                         (newdate, tag))
            sleep(0.5)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text='Вы успешно продлили абонемент'
            )
            ui.commit()

        # продление абонемента на год
        if call.data == 'year':
            sql1.execute("SELECT expired FROM users WHERE tag = ?", (tag,))
            date1 = sql1.fetchone()
            date = date1[0].split('.')
            date[2] = str(int(date[2]) + 1)
            newDate = f'{date[0]}.{date[1]}.{date[2]}'
            sql1.execute(f"UPDATE users SET expired = ? WHERE tag = ?",
                         (newDate, tag))
            sleep(0.5)
            client.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text='Вы успешно продлили абонемент'
            )
            ui.commit()

        # вывод расписания на сегодня
        if call.data == 'today':
            if datetime.datetime.today().weekday() == 6:
                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text='Сегодня выходной'
                )
            else:
                today = weekdays[datetime.datetime.today().weekday()]
                sql2.execute(
                    "SELECT name, time FROM practices WHERE day = ?",
                    (today,))
                result = sql2.fetchall()
                sendText = ''
                for names, times in result:
                    for i in range(len(names.split(' '))):
                        name = names.split(' ')[i]
                        time = times.split(' ')[i]
                        sendText += f'{name} - {time}\n'

                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text=sendText
                )

        # вывоод расписания на завтра
        if call.data == 'tomorrow':
            if datetime.datetime.today().weekday() == 6:
                tomorrow = 0
            else:
                tomorrow = weekdays[datetime.datetime.today().weekday() + 1]
            if tomorrow == 'воскресенье':
                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text='Сегодня выходной'
                )
            else:
                sql2.execute(
                    "SELECT name, time FROM practices WHERE day = ?",
                    (tomorrow,))
                result = sql2.fetchall()
                sendText = ''
                for names, times in result:
                    for i in range(len(names.split(' '))):
                        name = names.split(' ')[i]
                        time = times.split(' ')[i]
                        sendText += f'{name} - {time}\n'

                client.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.id,
                    text=sendText
                )


# запуск бота с беспрерывной работой и без задержки в отправке сообщений
client.polling(none_stop=True, interval=0)
