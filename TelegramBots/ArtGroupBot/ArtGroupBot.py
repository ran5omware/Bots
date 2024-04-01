# Импортируем используемые библиотеки
from telebot import *
import os
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Создаем бота и передаем ему токен
bot = telebot.TeleBot(TOKEN)

# Подключаем базу данных
conn = sqlite3.connect('main.db', check_same_thread=False)
cur = conn.cursor()
conn.commit()

# Задаем все константы и создаем словари
host_id = '1169465012'
users_status = {}
review_status = {}
order_status = {}
arts = 'Скетч Простой Детализированный Другое Оформление'
giveaway_start = '20.02 05.03 8.04 06.05 29.08 28.10'
giveaway_end = '23.02 08.03 11.04 09.05 1.09 31.10'
bigGiveaway_start = '25.05 25.12'
bigGiveaway_end = '01.06 01.01'
congratulations_start = False
congratulations_end = False
bigCongratulations_start = False
bigCongratulations_end = False


# Команда запуска бота
@bot.message_handler(commands=['start'])
def get_text(message):
    try:
        # Создаем таблицы в базе данных
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT,
            regDate TEXT,
            nickname TEXT,
            birthday TEXT,
            discount TEXT,
            rank TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS reviews (
            id TEXT,
            nickname TEXT,
            review TEXT
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS orders (
                    id TEXT,
                    username TEXT,
                    description TEXT
                )""")

        conn.commit()

    # Выводим ошибку при создании таблиц, если она есть
    except sqlite3.ProgrammingError as e:
        print(e)

    finally:
        # Создаем нашу клавиатуру и инлайн-кнопки в стартовом сообщении
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttonHelp = types.KeyboardButton(text="Мои возможности")
        buttonReg = types.KeyboardButton(text="Зарегистрироваться")
        buttonShow = types.KeyboardButton(text="Примеры работ")
        keyboard.add(buttonHelp, buttonReg, buttonShow)
        markup = types.InlineKeyboardMarkup()
        makeOrder = types.InlineKeyboardButton(
            text="Заказать арт",
            callback_data="Заказать арт"
        )
        links = types.InlineKeyboardButton(
            text="Ссылки на художника",
            callback_data="Ссылки на художника"
        )
        makeReview = types.InlineKeyboardButton(
            text="Оставить отзыв",
            callback_data="Оставить отзыв"
        )
        reviews = types.InlineKeyboardButton(
            text="Отзывы",
            callback_data="Отзывы"
        )
        price = types.InlineKeyboardButton(
            text="Прайс",
            callback_data="Прайс"
        )
        markup.add(price, makeOrder, makeReview, reviews, links)
        bot.send_message(
            message.chat.id,
            f"Привет, {message.from_user.username}",
            reply_markup=keyboard)
        bot.send_message(
            message.chat.id,
            'Выберите что вам надо',
            reply_markup=markup)
        conn.commit()


# Команда с инлайн-кнопками возможностей бота
@bot.message_handler(commands=['main'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    makeOrder = types.InlineKeyboardButton(
        text="Заказать арт",
        callback_data="Заказать арт"
    )
    links = types.InlineKeyboardButton(
        text="Ссылки на художника",
        callback_data="Ссылки на художника"
    )
    makeReview = types.InlineKeyboardButton(
        text="Оставить отзыв",
        callback_data="Оставить отзыв"
    )
    reviews = types.InlineKeyboardButton(
        text="Отзывы",
        callback_data="Отзывы"
    )
    price = types.InlineKeyboardButton(
        text="Прайс",
        callback_data="Прайс"
    )
    markup.add(price, makeOrder, makeReview, reviews, links)
    bot.send_message(
        message.chat.id,
        'Выберите что вам надо',
        reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text.lower() == "примеры работ")
def show_draws(message):
    markup = types.InlineKeyboardMarkup()
    sketch = types.InlineKeyboardButton(
        text="Скетч",
        callback_data="Скетч_пример"
    )
    simple = types.InlineKeyboardButton(
        text="Простой",
        callback_data="Простой_пример"
    )
    detail = types.InlineKeyboardButton(
        text="Детализированный",
        callback_data="Детализированный_пример"
    )
    different = types.InlineKeyboardButton(
        text="Другое",
        callback_data="Другое_пример"
    )
    design = types.InlineKeyboardButton(
        text="Оформление",
        callback_data="Оформление_пример"
    )
    markup.add(sketch, simple, detail, different, design)
    bot.send_message(
        chat_id=message.chat.id,
        text="Что вы хотите увидеть?",
        reply_markup=markup
    )


# Команда регистрации
@bot.message_handler(
    func=lambda message: message.text.lower() == 'зарегистрироваться')
def register(message):
    # Проверяем все ли данные ввел пользователь
    cur.execute(
        "SELECT id FROM users WHERE id=?",
        (message.chat.id,)
    )
    if not (cur.fetchone() is None):
        cur.execute(
            "SELECT birthday FROM users WHERE id=?",
            (message.chat.id,)
        )
        if cur.fetchone() is not None:
            cur.execute(
                "SELECT nickname FROM users WHERE id=?",
                (message.chat.id,)
            )
            bot.send_message(
                message.chat.id,
                f"{cur.fetchone()[0]}, вы уже зарегистрированы, но можете"
                f" сменить ник: /changename новый ник")
        else:
            bot.send_message(
                message.chat.id,
                f"{cur.fetchone()[0]}, вы уже вводили ник,"
                f" но не указали дату рождения,"
                f" пожалуйста, укажите сейчас.\nФормат: дд.мм\nПример: 10.05")
            users_status[message.chat.id] = "waiting_for_birthday"

    else:
        bot.send_message(message.chat.id, "Как вас называть?")
        # Устанавливаем состояние пользователя
        # как "waiting_for_name", чтобы обработать имя позднее
        users_status[message.chat.id] = "waiting_for_name"


# Стадия ввода и сохранения имени и даты регистрации
@bot.message_handler(
    func=lambda message: (
        message.chat.id in users_status and
        users_status[message.chat.id] == "waiting_for_name"
    )
)
def save_name(message):
    today = datetime.today().strftime('%d.%m.%y')
    cur.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
        (message.chat.id, today, message.text, '0', '0', 'F')
    )
    conn.commit()
    # Сбрасываем состояние пользователя
    users_status.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Введите день и месяц рождения(дд.мм)")
    # Устанавливаем состояние пользователя
    # как "waiting_for_birthday", чтобы обработать дату рождения позднее
    users_status[message.chat.id] = "waiting_for_birthday"


# Стадия ввода и сохранения даты рождения
@bot.message_handler(
    func=lambda message: (
            message.chat.id in users_status and
            users_status[message.chat.id] == "waiting_for_birthday"
    )
)
def save_birthday(message):
    # Проверяем на формат даты и сохраняем данные
    try:
        if datetime.strptime(message.text, '%d.%m'):
            cur.execute(
                "UPDATE users SET birthday=? WHERE id=?",
                (message.text, message.chat.id)
            )
            conn.commit()
            users_status.pop(message.chat.id, None)
            cur.execute(
                "SELECT nickname FROM users WHERE id=?",
                (message.chat.id,)
            )
            bot.send_message(
                message.chat.id,
                f"{cur.fetchone()[0]},"
                f" вы успешно зарегистрировались"
            )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Похоже вы ввели дату рождения неправильно, попробуйте еще раз.\n"
            "Формат ввода: дд.мм\nПример: 10.05")


# Хелп-команда
@bot.message_handler(
    func=lambda message:
    (message.text.lower() == "мои возможности"
     or message.text.lower() in "помощь help")
)
def make_help(message):
    # Вывод информации о возможностях бота
    text = (f"Чтобы зарегистрироваться, введите *Зарегистрироваться*\n"
            f"Чтобы сменить ник, введите /changename новый ник\n"
            f"Чтобы показать все команды нажмите -> /main")
    bot.send_message(message.chat.id, text)


# Стадия сохранения отзыва
@bot.message_handler(
    func=lambda message:
    (message.chat.id in review_status and
     review_status[message.chat.id] == "waiting_for_text")
)
def save_review(message):
    cur.execute(
        "SELECT nickname FROM users WHERE id=?",
        (message.chat.id,)
    )
    nickname = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO reviews VALUES (?, ?, ?)",
        (message.chat.id, nickname, message.text)
    )
    bot.send_message(message.chat.id, "Спасибо за ваш отзыв!")
    review_status.pop(message.chat.id, None)


# Стадия сохранения заказа и отправки ее художнику
@bot.message_handler(
    func=lambda message: (
            message.chat.id in order_status and
            order_status[message.chat.id] in arts
    )
)
def save_order(message):
    username = message.from_user.username
    description = (f"Заказ: {order_status[message.chat.id]},"
                   f" описание: {message.text}")
    cur.execute(
        "INSERT INTO orders VALUES (?, ?, ?)",
        (message.chat.id, username, description)
    )
    bot.send_message(
        message.chat.id,
        "Спасибо за ваш заказ, ожидайте сообщения от художника"
    )
    bot.send_message(
        host_id,
        f"{username} заказал {order_status[message.chat.id]}, "
        f"описание: {message.text}"
    )
    order_status.pop(message.chat.id, None)


# Обработка остальных сообщений и создание розыгрыша, выдача рангов
@bot.message_handler(content_types=["text"])
def other_messages(message):
    global congratulations_start, congratulations_end
    global bigCongratulations_start, bigCongratulations_end
    cur.execute(
        "SELECT birthday FROM users WHERE id=?",
        (message.chat.id,)
    )
    today = datetime.today().strftime('%d.%m')
    # Поздравление с днем рождения
    if cur.fetchone()[0] == today:
        link = (
            'http://api.giphy.com/v1/gifs/random?'
            'api_key=POnmtmurHtU62MeLkX16PCrPMCOqRbhS&tag=happy%20birthday')
        response = requests.get(link)
        data = response.json()
        gif = data['data']['images']['original']['url']
        bot.send_message(message.chat.id, "Поздравляю с днем рождения!!!")
        bot.send_document(message.chat.id, gif)
    # Начало маленького розыгрыша
    if today in giveaway_start and not congratulations_start:
        cur.execute("SELECT id FROM users")
        users = [row[0] for row in cur.fetchall()]
        for user in users:
            bot.send_message(
                user,
                f"В придверии праздника начинаем очередной розыгрыш!\n"
                f"Победитель получит бесплатный рисунок по его заказу!!!\n"
                f"Условия просты - подписка на группу https://t.me/lulusikkk")
        congratulations_start = True
    if today not in giveaway_start:
        congratulations_start = False
    # Конец маленького розыгрыша
    if today in giveaway_end and not congratulations_end:
        cur.execute("SELECT nickname FROM users")
        users = [row[0] for row in cur.fetchall()]
        winner = random.choice(users)
        cur.execute("SELECT id FROM users")
        users = [row[0] for row in cur.fetchall()]
        for user in users:
            bot.send_message(
                user,
                f"Вот и пришла пора подводить итоги розыгрыша!\n"
                f"А победителем на этот раз становится - {winner}!\n"
                f"Поздравляем его. "
                f"Чтобы получить выигрыш напиши"
                f" художнику - https://t.me/Lulis1k"
            )
        congratulations_end = True
    if today not in giveaway_end:
        congratulations_end = False
    # Начало большого розыгрыша
    if today in bigGiveaway_start and not bigCongratulations_start:
        cur.execute("SELECT id FROM users")
        users = [row[0] for row in cur.fetchall()]
        for user in users:
            bot.send_message(
                user,
                f"В придверии смены времени года"
                f" начинаем очередной розыгрыш!\n"
                f"Победитель получит бесплатный"
                f" полноценный рисунок по его заказу!!!\n"
                f"Условия просты - подписка"
                f" на группу https://t.me/lulusikkk")
        bigCongratulations_start = True
    if today not in bigGiveaway_start:
        bigCongratulations_start = False
    # Конец большого розыгрыша
    if today in bigGiveaway_end and not bigCongratulations_end:
        cur.execute("SELECT nickname FROM users")
        users = [row[0] for row in cur.fetchall()]
        winner = random.choice(users)
        cur.execute("SELECT id FROM users")
        users = [row[0] for row in cur.fetchall()]
        for user in users:
            bot.send_message(
                user,
                f"Вот и пришла пора подводить итоги розыгрыша!\n"
                f"А победителем на этот раз становится - {winner}!\n"
                f"Поздравляем его. "
                f"Чтобы получить выигрыш напиши"
                f" художнику - https://t.me/Lulis1k")
        bigCongratulations_end = True
    if today not in bigGiveaway_end:
        bigCongratulations_end = False
    cur.execute(
        "SELECT regDate FROM users WHERE id=?",
        (message.chat.id,)
    )
    # Проверка на время регистрации и выдача рангов
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    if int(day) - 3 < 1:
        if int(month) == 1:
            month = 12
        day = 31 - (3 - int(day))
    else:
        day = int(day) - 3
    if int(day) < 10:
        date = f"0{day}.{month}.{year}"
    else:
        date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('E', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Вы с нами уже 3 дня, ваш ранг повысился до E"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    if int(day) - 7 < 1:
        if int(month) == 1:
            month = 12
        day = 31 - (7 - int(day))
    else:
        day = int(day) - 7
    if int(day) < 10:
        date = f"0{day}.{month}.{year}"
    else:
        date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('D', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Вы с нами уже неделю, ваш ранг повысился до D"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    if int(month) == 1:
        month = 12
    else:
        month = int(month) - 1
    if int(month) < 10:
        date = f"{day}.0{month}.{year}"
    else:
        date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('C', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Вы с нами уже месяц, ваш ранг повысился до C"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    if int(month) - 3 < 1:
        month = 12 - (3 - int(month))
    else:
        month = int(month) - 3
    if int(month) < 10:
        date = f"{day}.0{month}.{year}"
    else:
        date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('B', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Вы с нами уже 3 месяца, ваш ранг повысился до B"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    if int(month) - 6 < 1:
        month = 12 - (6 - int(month))
        year = int(year) - 1
    else:
        month = int(month) - 6
    if int(month) < 10:
        date = f"{day}.0{month}.{year}"
    else:
        date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET discount=? WHERE id=?",
            ('10', message.chat.id)
        )
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('A', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Ура!!! Вы с нами уже полгода,"
            " теперь ваш ранк - A, в честь этого"
            " вы получаете постоянную скидку 10%"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    year = int(year) - 1
    date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET discount=? WHERE id=?",
            ('15', message.chat.id)
        )
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('S', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Ура!!! Вы с нами уже год,"
            " теперь ваш ранк - S, в честь этого"
            " вы получаете постоянную скидку 15%"
        )
    day, month, year = datetime.today().strftime('%d.%m.%y').split('.')
    year = int(year) - 2
    date = f"{day}.{month}.{year}"
    if cur.fetchone()[0] == date:
        cur.execute(
            "UPDATE users SET discount=? WHERE id=?",
            ('20', message.chat.id)
        )
        cur.execute(
            "UPDATE users SET rank=? WHERE id=?",
            ('SS', message.chat.id)
        )
        bot.send_message(
            message.chat.id,
            "Ура!!! Вы с нами уже 2 года,"
            " теперь ваш ранк - SS, в честь этого"
            " вы получаете постоянную скидку 20%"
        )


# Обработка инлайн-кнопки "Оставить отзыв"
@bot.callback_query_handler(func=lambda call: call.data == "Оставить отзыв")
def make_review(call):
    cur.execute(
        "SELECT id FROM orders WHERE id=?",
        (call.message.chat.id,)
    )
    if cur.fetchone():
        cur.execute(
            "SELECT id FROM reviews WHERE id=?",
            (call.message.chat.id,)
        )
        if cur.fetchone():
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text="Вы уже оставляли отзыв"
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                text="Введите отзыв"
            )
            review_status[call.message.chat.id] = "waiting_for_text"
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text="Сначала сделайте заказ"
        )


# Обработка инлайн-кнопки "Ссылки на художника"
@bot.callback_query_handler(
    func=lambda call: call.data == "Ссылки на художника")
def send_links(call):
    links = ("VK: https://vk.com/1l0v3yara\n"
             "VK группа: https://vk.com/lulus1k\n"
             "TG: https://t.me/Lulis1k\n"
             "TG группа: https://t.me/lulusikkk")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=links
    )


# Обработка инлайн-кнопки "Прайс"
@bot.callback_query_handler(func=lambda call: call.data == "Прайс")
def price_list(call):
    prices = ("Прайс:\n\n"
              "- Скетч - 300 р\n"
              "- Арт средней сложности (1 персонаж, простой фон) - 400 р\n"
              "- Полноценный арт с фоном(1 персонаж, детализация) - 700 р\n"
              "- За каждого дополнительного персонажа  +400 р\n"
              "-Другое(иконки для игр, фоны, чиби-персонажи)"
              " - писать в лс художнику\n\n"
              "Оформление для вк:\n"
              "- Баннер - 700 р\n"
              "- Оформление разделов - 500 р за каждый раздел")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=prices
    )


# Обработка инлайн-кнопки "Отзывы"
@bot.callback_query_handler(func=lambda call: call.data == "Отзывы")
def show_reviews(call):
    cur.execute("SELECT nickname, review FROM reviews")
    rows = cur.fetchall()
    if rows:
        text = ''
        for row in rows:
            nickname, review = row
            text += f'{nickname} пишет: "{review}".\n'
        bot.send_message(chat_id=call.message.chat.id, text="Отзывы:")
        bot.send_message(chat_id=call.message.chat.id, text=text)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text="Отзывов пока нет("
        )


# Обработка инлайн-кнопки "Заказать арт"
@bot.callback_query_handler(
    func=lambda call: call.data == "Заказать арт"
)
def make_order(call):
    markup = types.InlineKeyboardMarkup()
    sketch = types.InlineKeyboardButton(
        text="Скетч",
        callback_data="Скетч"
    )
    simple = types.InlineKeyboardButton(
        text="Простой",
        callback_data="Простой"
    )
    detail = types.InlineKeyboardButton(
        text="Детализированный",
        callback_data="Детализированный"
    )
    different = types.InlineKeyboardButton(
        text="Другое",
        callback_data="Другое"
    )
    design = types.InlineKeyboardButton(
        text="Оформление",
        callback_data="Оформление"
    )
    markup.add(sketch, simple, detail, different, design)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Что вы хотите заказать?",
        reply_markup=markup
    )


# Заказ скетча
@bot.callback_query_handler(func=lambda call: call.data == "Скетч")
def order_sketch(call):
    global order_status
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Напишите, что вы хотите видеть на рисунке"
             " или пришлите ссылку на imgur с фотографией"
    )
    order_status[call.message.chat.id] = call.data


# Заказ простого арта
@bot.callback_query_handler(func=lambda call: call.data == "Простой")
def order_simple(call):
    global order_status
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Напишите, что вы хотите видеть на рисунке"
             " или пришлите ссылку на imgur с фотографией"
    )
    order_status[call.message.chat.id] = call.data


# Заказ детализированного арта
@bot.callback_query_handler(func=lambda call: call.data == "Детализированный")
def order_detail(call):
    global order_status
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Напишите, что вы хотите видеть на рисунке"
             " или пришлите ссылку на imgur с фотографией"
    )
    order_status[call.message.chat.id] = call.data


# Заказ чего-то другого(иконки, банеры и т.п)
@bot.callback_query_handler(func=lambda call: call.data == "Другое")
def order_other(call):
    global order_status
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Напишите, что вы хотите"
             " или пришлите ссылку на imgur с фотографией"
    )
    order_status[call.message.chat.id] = call.data


# Заказ оформления
@bot.callback_query_handler(func=lambda call: call.data == "Оформление")
def order_design(call):
    global order_status
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Напишите, что вы хотите видеть"
             " или пришлите ссылку на imgur с фотографией"
    )
    order_status[call.message.chat.id] = call.data


# Пример скетча
@bot.callback_query_handler(func=lambda call: call.data == "Скетч_пример")
def example_sketch(call):
    with open('sketch.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
        bot.send_message(call.message.chat.id, "Скетч")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )


# Пример простого арта
@bot.callback_query_handler(func=lambda call: call.data == "Простой_пример")
def example_simple(call):
    with open('simple.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
        bot.send_message(call.message.chat.id, "Простой арт")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )


# Пример детализированного арта
@bot.callback_query_handler(
    func=lambda call: call.data == "Детализированный_пример")
def example_detail(call):
    with open('detail.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
        bot.send_message(call.message.chat.id, "Детализированный арт")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )


# Пример иконки, банера и т.п
@bot.callback_query_handler(func=lambda call: call.data == "Другое_пример")
def example_other(call):
    with open('icon.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
        bot.send_message(call.message.chat.id, "Иконка")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )


# Пример оформления
@bot.callback_query_handler(func=lambda call: call.data == "Оформление_пример")
def example_design(call):
    with open('banner.jpg', 'rb') as photo:
        bot.send_photo(call.message.chat.id, photo)
        bot.send_message(call.message.chat.id, "Банер для вк")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=call.message.text
        )


bot.polling(none_stop=True, interval=0)
