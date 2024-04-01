# Импорт библиотек
from telebot import *
import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

# Инициализация бота
bot = telebot.TeleBot(os.getenv('TOKEN'))

# Подключение к базе данных SQLite
con = sqlite3.connect('movies.db', check_same_thread=False)
c = con.cursor()
con.commit()

# Инициализация словаря для хранения запросов пользователя
user_request = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global user_request
    c.execute("""CREATE TABLE IF NOT EXISTS movies (
        name TEXT,
        genre TEXT,
        format TEXT,
        country TEXT,
        type TEXT,
        age TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS actors (
            movie TEXT,
            actor TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        movie TEXT,
        review INTEGER
    )""")
    con.commit()

    # Сброс фильтров при старте бота
    user_request = {
        "type": '',
        "genre": '',
        "format": '',
        "country": '',
        "age": ''
    }

    # Запрос к сайту giphy для получения гиф-изображения
    link = ('http://api.giphy.com/v1/'
            'gifs/random?api_key=K3XvsRsOcwKZvCBngWrdsDoW7IrQA9Pe'
            '&tag=hello')
    response = requests.get(link)
    data = response.json()
    gif = data['data']['images']['original']['url']

    # Создание клавиатуры с помощью кнопок
    # и отправка приветственного сообщения с клавиатурой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_command = types.KeyboardButton("Помощь")
    reset = types.KeyboardButton("Сбросить фильтры")
    keyboard.add(help_command, reset)
    text = "Приветствую, я помогу найти, что посмотреть"

    bot.send_message(message.chat.id, text, reply_markup=keyboard)
    bot.send_document(message.chat.id, gif)


# Обработчик команды /movie_type
@bot.message_handler(commands=['movie_type'])
def movie_type(message):
    keyboard = types.InlineKeyboardMarkup()
    movie = types.InlineKeyboardButton(
        text="Фильм",
        callback_data="фильм")
    series = types.InlineKeyboardButton(
        text="Сериал",
        callback_data="сериал")
    keyboard.add(movie, series)
    bot.send_message(
        message.chat.id,
        "Выберите тип контента",
        reply_markup=keyboard)


# Обработчик команды /movie_age
@bot.message_handler(commands=['movie_age'])
def movie_age(message):
    keyboard = types.InlineKeyboardMarkup()
    zero_plus = types.InlineKeyboardButton(
        text="0+",
        callback_data="0+")
    six_plus = types.InlineKeyboardButton(
        text="6+",
        callback_data="6+")
    twelve_plus = types.InlineKeyboardButton(
        text="12+",
        callback_data="12+")
    sixteen_plus = types.InlineKeyboardButton(
        text="16+",
        callback_data="16+")
    eighteen_plus = types.InlineKeyboardButton(
        text="18+",
        callback_data="18+")
    keyboard.add(
        zero_plus,
        six_plus,
        twelve_plus,
        sixteen_plus,
        eighteen_plus)
    bot.send_message(
        message.chat.id,
        "Выберите тип контента",
        reply_markup=keyboard)


# Обработчик команды /movie_genre
@bot.message_handler(commands=['movie_genre'])
def movie_genre(message):
    keyboard = types.InlineKeyboardMarkup()
    comedy = types.InlineKeyboardButton(
        text="Комедия",
        callback_data="комедия")
    action = types.InlineKeyboardButton(
        text="Боевик",
        callback_data="боевик")
    drama = types.InlineKeyboardButton(
        text="Драма",
        callback_data="драма")
    detective = types.InlineKeyboardButton(
        text="Детектив",
        callback_data="детектив")
    horror = types.InlineKeyboardButton(
        text="Ужасы",
        callback_data="ужасы")
    fantasy = types.InlineKeyboardButton(
        text="Фэнтези",
        callback_data="фэнтези")
    keyboard.add(comedy, action, drama, detective, horror, fantasy)
    bot.send_message(
        message.chat.id,
        "Выберите жанр",
        reply_markup=keyboard)


# Обработчик команды /movie_country
@bot.message_handler(commands=['movie_country'])
def movie_country(message):
    keyboard = types.InlineKeyboardMarkup()
    ussr = types.InlineKeyboardButton(
        text="СССР",
        callback_data="СССР")
    russia = types.InlineKeyboardButton(
        text="Россия",
        callback_data="Россия")
    usa = types.InlineKeyboardButton(
        text="США",
        callback_data="США")
    eu = types.InlineKeyboardButton(
        text="Европа",
        callback_data="Европа")
    keyboard.add(ussr, russia, usa, eu)
    bot.send_message(
        message.chat.id,
        "Выберите страну",
        reply_markup=keyboard)


# Обработчик команды /movie_format
@bot.message_handler(commands=['movie_format'])
def movie_format(message):
    if user_request['type'] == "сериал":
        bot.send_message(message.chat.id, "У вас выбран сериал")
        user_request['format'] = "сериал"
    else:
        keyboard = types.InlineKeyboardMarkup()
        short = types.InlineKeyboardButton(
            text="Короткометражный",
            callback_data="короткометражный")
        full = types.InlineKeyboardButton(
            text="Полнометражный",
            callback_data="полнометражный")
        keyboard.add(short, full)
        bot.send_message(
            message.chat.id,
            "Выберите формат",
            reply_markup=keyboard)


# Обработчик команды /movie_find
@bot.message_handler(commands=['movie_find'])
def movie_find(message):
    try:
        sql_request = "SELECT * FROM movies WHERE "
        conditions = []

        for key, value in user_request.items():
            if value != "":
                conditions.append(f"{key}='{value}'")

        if conditions:
            sql_request += " AND ".join(conditions)
        c.execute(sql_request)
    except Exception as e:
        # Обработчик ошибок
        print(e)
        text = "Фильтры пустые, не могу ничего найти"
        bot.send_message(message.chat.id, text)
        return
    finally:
        # Выводим все подходящие под фильтры фильмы и сериалы, если они есть
        result = c.fetchall()

        if result:
            for movie in result:
                if movie[4] == 'сериал':
                    text = (f"{movie[4]} '{movie[0]}'"
                            f"\nВозрастной рейтинг: {movie[5]}"
                            f"\nЖанр: {movie[1]}"
                            f"\nСтрана: {movie[3]}")
                else:
                    text = (f"{movie[4]} '{movie[0]}'"
                            f"\nФормат: {movie[2]}"
                            f"\nВозрастной рейтинг: {movie[5]}"
                            f"\nЖанр: {movie[1]}"
                            f"\nСтрана: {movie[3]}")
                bot.send_message(message.chat.id, text)
        else:
            text = "Фильмы и сериалы по вашему запросу не найдены"
            bot.send_message(message.chat.id, text)


# Обработчик команды /show_actors
@bot.message_handler(commands=['show_actors'])
def show_actors(message):
    try:
        # Ищем в базе данных актеров по названию фильма или сериала
        test = message.text.split(' ')[1]
        name = message.text.split(' ')[1:]
        name = ' '.join([i.lower() for i in name])
        c.execute("SELECT actor FROM actors WHERE movie=?", (name,))
        result = c.fetchone()
        if result:
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Такой фильм/сериал не найден")
    except Exception as e:
        # Обработчик ошибок
        print(e)
        text = ("Ошибка, возможно вы не указали название. "
                "Пример команды: /show_actors игра престолов")
        bot.send_message(message.chat.id, text)


# Обработчик команды /make_review
@bot.message_handler(commands=['make_review'])
def make_review(message):
    try:
        # Заносим в базу данных отзыв на фильм или сериал, если его еще нет
        review = message.text.split(' ')[1]
        name = message.text.split(' ')[2:]
        name = ' '.join([i.lower() for i in name])
        c.execute("SELECT review FROM reviews WHERE movie=?", (name,))
        if c.fetchone():
            bot.send_message(
                message.chat.id,
                "У вас уже оставлен отзыв на этот фильм/сериал")
        else:
            c.execute(
                "INSERT INTO reviews (movie, review) VALUES (?, ?)",
                (name, review))
            bot.send_message(message.chat.id, "Готово")
            con.commit()
    except Exception as e:
        # Обработчик ошибок
        print(e)
        text = ("Ошибка, возможно вы не указали оценку или название. "
                "Пример команды: /make_review 10 игра престолов")
        bot.send_message(message.chat.id, text)


# Обработчик команды /show_watched
@bot.message_handler(commands=['show_watched'])
def show_watched(message):
    try:
        # Выводим из базы данных все фильмы, на которых стоят оценки
        c.execute("SELECT movie, review FROM reviews")
        text = ''
        names = c.fetchall()
        for name, review in names:
            text += name + ' - ' + str(review) + "\n"
        bot.send_message(message.chat.id, text)
    except Exception as e:
        # Обработчик ошибок
        print(e)
        text = ("Ошибка, возможно у вас еще нет просмотренных, "
                "отметить просмотренным и поставить оценку -> /make_review")
        bot.send_message(message.chat.id, text)


# Обработчик callback'ов для занесения данных в словарь фильтров
@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    if call.data == "фильм" or call.data == "сериал":
        user_request["type"] = call.data
        bot.edit_message_text(
            message_id=call.message.id,
            chat_id=call.message.chat.id,
            text=f"Вы выбрали {call.data}")
    if call.data in "0+ 6+ 12+ 16+ 18+":
        user_request["age"] = call.data
        bot.edit_message_text(
            message_id=call.message.id,
            chat_id=call.message.chat.id,
            text=f"Вы выбрали {call.data}")
    if call.data in "комедия боевик драма детектив ужасы фэнтези":
        user_request["genre"] = call.data
        bot.edit_message_text(
            message_id=call.message.id,
            chat_id=call.message.chat.id,
            text=f"Вы выбрали {call.data}")
    if call.data in "СССР Россия США Европа":
        user_request["country"] = call.data
        bot.edit_message_text(
            message_id=call.message.id,
            chat_id=call.message.chat.id,
            text=f"Вы выбрали {call.data}")
    if call.data in 'полнометражный короткометражный':
        user_request["format"] = call.data
        bot.edit_message_text(
            message_id=call.message.id,
            chat_id=call.message.chat.id,
            text=f"Вы выбрали {call.data}")


# Обработчик команды /help и /reset_filters
@bot.message_handler(content_types=['text'])
def message_handler(message):
    global user_request
    if message.text == "Помощь":
        text = """
/start - перезапустить бота
/movie_type - указать, найти фильм или сериал
/movie_age - указать возрастной рейтинг
/movie_genre - указать жанр
/movie_country - указать страну (США, Россия т.п)
/movie_format - указать формат (полнометражный/короткометражный)
/movie_find - найти фильм или сериал по указанным ранее параметрам
/show_actors - указать актеров из фильма или сериала
/make_review - поставить оценку просмотренному фильму или сериалу
/show_watched - показать просмотренные фильмы и сериалы
        """
        bot.send_message(message.chat.id, text)
    elif message.text == "Сбросить фильтры":
        user_request = {
            "type": '',
            "genre": '',
            "format": '',
            "country": '',
            "age": ''
        }
        bot.send_message(message.chat.id, "Фильтры успешно сброшены")


# Запуск бота
bot.polling()
