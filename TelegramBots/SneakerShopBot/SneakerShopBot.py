# Импорт библиотек
from telebot import *
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

telebot = telebot.TeleBot(os.getenv('TOKEN'))

user_ids = []
cheque_ids = []


# Команда старт
@telebot.message_handler(commands=['start'])
def start_command(message):
    telebot.send_message(
        message.chat.id,
        "Привет! Я бот менеджер магазина кросовок, позволяющий"
        " следить за ассортиментом и продажами")
    telebot.send_message(message.chat.id, "/help для просмотр команд")
    link = ('http://api.giphy.com/v1/gifs/random?'
            'api_key=rlDW02wK9uxxfGLMavjGnQ1aAYKuuHgl&tag=приветствие')
    response = requests.get(link)
    data = response.json()
    gif = data['data']['images']['original']['url']
    telebot.send_document(message.chat.id, gif)
    # Заполняем массивы id
    with open('clients.json', mode='r', encoding='utf-8') as clients:
        data = json.load(clients)
    for key, item in data['client_id'].items():
        user_ids.append(key)
    with open('sales.json', mode='r', encoding='utf-8') as sales:
        data = json.load(sales)
    for key, item in data['client_id'].items():
        for key2, item2 in item.items():
            cheque_ids.append(key2)


# Команда хелп
@telebot.message_handler(commands=['help'])
def help_command(message):
    telebot.send_message(message.chat.id, """Доступные команды:
/assortment - просмотр ассортимента
/add_product - добавить новый товар в ассортимент
/delete_product - удалить товар из ассортимента
/change_price - изменить цену на товар
/change_availability - изменить количество товара
/product_search - поиск товара по названию
/show_sales - просмотр статистики по продажам
/add_client - добавление информации о клиенте
/add_sell - запись информации, о покупке клиента
/show_clients - просмотр информации по клиентам""")


# Команда ассортмента
@telebot.message_handler(commands=['assortment'])
def assortment(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
        prices = ''
        # Проходясь по всем значениям выводим товар
        # с ценой, количеством и артиклем
        for brand, models in data['brand'].items():
            prices += f'{brand}\n\n'
            for article, details in models.items():
                model = details[0]
                cost = details[1]
                count = details[2]
                if int(count) == 0:
                    count = 'Законился'
                    prices += f'{model} - {count}'
                else:
                    prices += (f'{model} - {cost} руб.'
                               f' / {count}шт. / артикул: {article}\n')
            prices += '\n\n\n'
        telebot.send_message(message.chat.id, prices)


# Команда добавления товара
@telebot.message_handler(commands=['add_product'])
def add_product(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
    text = message.text.split(';')[1:]
    try:
        brand = text[0]
        article = text[1]
        model = text[2]
        cost = text[3]
        count = text[4]
        int(cost)
        int(count)
        # Если заданого бренда не существует в нашем файле, то
        # создаем его и добавляем туда модель
        if brand not in data['brand']:
            data['brand'][brand] = {}
        data['brand'][brand][article] = [model, cost, count, '0']
        with open('products.json', mode='w', encoding='utf-8') as products:
            json.dump(data, products, ensure_ascii=False, indent=4)
        telebot.send_message(message.chat.id, 'Модель успешно добавлена')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /add_product ;марка;артикул;модель;цена;количество\n'
            'Пример: /add_product ;Nike;FQ8225-100;Nike '
            'Air Trainer 1 Essential;20999;10')


# Команда удаления товара
@telebot.message_handler(commands=['delete_product'])
def delete_product(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
    text = message.text.split(';')[1:]
    try:
        # Проверка на существование и удаление
        brand = text[0]
        article = text[1]
        if brand not in data['brand']:
            telebot.send_message(message.chat.id, 'Бренд не найден')
        elif article not in data['brand'][brand]:
            telebot.send_message(message.chat.id, 'Артикул не найден')
        else:
            del data['brand'][brand][article]
            with open('products.json', mode='w', encoding='utf-8') as products:
                json.dump(data, products, ensure_ascii=False, indent=4)
            telebot.send_message(message.chat.id, 'Модель успешно удалена')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /delete_product ;марка;артикул\n'
            'Пример: /delete_product ;Nike;FQ8225-100')


# Команда смены цены товара
@telebot.message_handler(commands=['change_price'])
def change_price(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
    text = message.text.split(';')[1:]
    try:
        # Проверка на существование и изменение цены
        brand = text[0]
        article = text[1]
        cost = text[2]
        if brand not in data['brand']:
            telebot.send_message(message.chat.id, 'Бренд не найден')
        elif article not in data['brand'][brand]:
            telebot.send_message(message.chat.id, 'Артикул не найден')
        else:
            model = data['brand'][brand][article]
            model[1] = cost
            data['brand'][brand][article] = model
            with open('products.json', mode='w', encoding='utf-8') as products:
                json.dump(data, products, ensure_ascii=False, indent=4)
            telebot.send_message(message.chat.id, 'Цена успешно изменена')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /change_price ;марка;артикул;новая цена\n'
            'Пример: /change_price ;Nike;FQ8225-100;21999')


# Команда смены количества товара
@telebot.message_handler(commands=['change_availability'])
def change_availability(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
    text = message.text.split(';')[1:]
    try:
        # Проверка на существование и изменение количества
        brand = text[0]
        article = text[1]
        count = text[2]
        if brand not in data['brand']:
            telebot.send_message(message.chat.id, 'Бренд не найден')
        elif article not in data['brand'][brand]:
            telebot.send_message(message.chat.id, 'Артикул не найден')
        else:
            model = data['brand'][brand][article]
            model[2] = count
            data['brand'][brand][article] = model
            with open('products.json', mode='w', encoding='utf-8') as products:
                json.dump(data, products, ensure_ascii=False, indent=4)
            telebot.send_message(
                message.chat.id,
                'Количество успешно изменено')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /change_availability ;марка;артикул;количество\n'
            'Пример: /change_availability ;Nike;FQ8225-100;20')


# Команда поиска товара по названию
@telebot.message_handler(commands=['product_search'])
def product_search(message):
    with open('products.json', mode='r', encoding='utf-8') as products:
        data = json.load(products)
    text = message.text.split(';')[1:]
    flag = False
    try:
        # Проверка на существование и передача flag = True в случае нахождения
        model = text[0]
        for brand, models in data['brand'].items():
            for article, details in models.items():
                if model in details[0]:
                    prices = (f'{model} - {details[1]} руб. /'
                              f' {details[2]}шт. / артикул: {article}\n')
                    telebot.send_message(message.chat.id, prices)
                    flag = True
        # Если не нашлось
        if not flag:
            telebot.send_message(message.chat.id, f'Модель {model} не найдена')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /product_search ;модель\n'
            'Пример: /product_search ;Nike Air Trainer 1 Essential')


# Команда добавления клиента
@telebot.message_handler(commands=['add_client'])
def add_product(message):
    with open('clients.json', mode='r', encoding='utf-8') as clients:
        data = json.load(clients)
    text = message.text.split(';')[1:]
    try:
        # Создаем нового клиента
        client_id = max(user_ids) + 1
        name = text[0]
        sales = text[1]
        data['client_id'][client_id] = {}
        data['client_id'][client_id] = [name, sales]
        with open('clients.json', mode='w', encoding='utf-8') as clients:
            json.dump(data, clients, ensure_ascii=False, indent=4)
        telebot.send_message(message.chat.id, 'Клиент успешно добавлен')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /add_client ;имя;количество покупок\n'
            'Пример: /add_client ;Иванов Иван Иванович;2')


# Команда добавления продажи
@telebot.message_handler(commands=['add_sell'])
def add_sell(message):
    with open('sales.json', mode='r', encoding='utf-8') as sales:
        data = json.load(sales)
    text = message.text.split(';')[1:]
    try:
        client_id = text[0]
        name = text[1]
        cheque_id = max(cheque_ids)
        date = datetime.today().strftime('%d.%m.%y')
        article = text[2]
        cost = text[3]
        count = text[4]
        # Добавляем новый чек
        if client_id not in data['client_id']:
            data['client_id'][client_id] = {}
        if cheque_id not in data['client_id'][client_id]:
            data['client_id'][client_id][cheque_id] = {}
        data['client_id'][client_id][cheque_id] = [date, article, cost, count]
        with open('sales.json', mode='w', encoding='utf-8') as sales:
            json.dump(data, sales, ensure_ascii=False, indent=4)
        # Обновляем информацию о клиентах
        with open('clients.json', mode='r', encoding='utf-8') as clients:
            data = json.load(clients)
            if client_id in data['client_id']:
                old_count = data['client_id'][client_id][1]
                data['client_id'][client_id] = [name, old_count + count]
            else:
                data['client_id'][client_id] = {}
                data['client_id'][client_id] = [name, count]
        with open('clients.json', mode='w', encoding='utf-8') as clients:
            json.dump(data, clients, ensure_ascii=False, indent=4)
        # Уменьшаем количество товара на то, сколько купили
        with open('products.json', mode='r', encoding='utf-8') as products:
            data = json.load(products)
            for brand, models in data['brand'].items():
                for art, details in models.items():
                    if art == article:
                        model = data['brand'][brand][article]
                        model[2] = str(int(model[2]) - int(count))
        # Добавление чека
        with open('products.json', mode='w', encoding='utf-8') as products:
            json.dump(data, products, ensure_ascii=False, indent=4)
        telebot.send_message(message.chat.id, 'Чек успешно добавлен')
    except Exception as e:
        # Если где-то в функции вышла ошибка, то отправляем пасту с командой
        print(e)
        telebot.send_message(
            message.chat.id,
            'Введите /add_sell ;id клиента;имя клиента;'
            'артикул товара;цена;количество\n'
            'Пример: /add_sell ;4;Иванов Иван Иванович;'
            '56;FQ8225-100;20999;1')


# Команда просмотра всех клиентов
@telebot.message_handler(commands=['show_clients'])
def show_clients(message):
    with open('clients.json', mode='r', encoding='utf-8') as clients:
        data = json.load(clients)
        show = ''
        # Проходимся по всем клиентам и выводим их
        for client_id, client in data['client_id'].items():
            show += (f'{client[0]} с id {client_id}'
                     f' купил {client[1]} товара(-ов)\n')
            show += '\n'
        telebot.send_message(message.chat.id, show)


# Команда просмотра всех продаж
@telebot.message_handler(commands=['show_sales'])
def show_sales(message):
    # Проходимся по всем продажам и выводим их
    with open('sales.json', mode='r', encoding='utf-8') as sales:
        data = json.load(sales)
        show = ''
        for client_id, client in data['client_id'].items():
            for cheque_id, cheque in client.items():
                show += (f'Клиент с id {client_id} {cheque[0]}'
                         f' купил товар {cheque[1]} в количестве {cheque[3]}'
                         f'шт на сумму {cheque[2]}. Чек номер {cheque_id}\n')
                show += '\n'
        telebot.send_message(message.chat.id, show)


# Запуск бота
telebot.polling(none_stop=True, interval=0)
