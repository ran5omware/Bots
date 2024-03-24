import os
from dotenv import load_dotenv
import disnake
import asyncio
import sqlite3
from disnake.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all())

conn = sqlite3.connect('filters.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS text_filters 
             (channel_id INTEGER PRIMARY KEY, filters TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS link_filters 
             (channel_id INTEGER PRIMARY KEY, filters TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS roles 
             (role TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS guest_filters 
             (server INTEGER PRIMARY KEY, filters TEXT)''')

conn.commit()


def link_checker(message):
    c.execute("SELECT filters FROM link_filters WHERE channel_id = ?", (message.channel.id,))
    row = c.fetchone()
    if row:
        filters = row[0].split(';')
        if message.content.startswith("http://") or message.content.startswith("https://"):
            flag = True
            for word in filters:
                if word == message.content.split('/')[2]:
                    flag = False
            return flag


def text_checker(message):
    c.execute("SELECT filters FROM text_filters WHERE channel_id = ?", (message.channel.id,))
    row = c.fetchone()
    if row:
        text_filters = row[0].split(';')
        flag = True
        if message.content.split(' ')[0] in text_filters:
            flag = False
        return flag


def guest_checker(message):
    c.execute("SELECT filters FROM guest_filters WHERE server = ?", (1,))
    row = c.fetchone()
    if row:
        guest_filters = row[0].split(';')
        flag = False
        if (message.content.split(' ')[0] in guest_filters) or ('/' in message.content):
            flag = True
        return flag


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")


@bot.event
async def on_message(message):
    result = False
    for role in message.author.roles:
        c.execute("SELECT * FROM roles WHERE role=?", (role.id,))
        result = c.fetchone()
        if result:
            break
    if result:
        if guest_checker(message):
            await message.delete()
            await message.channel.send(f'*Эта команда доступна только для авторизованных участников сервера, пожалуйста авторизуйтесь и получите роль "Участник"')
        return
    elif message.author == message.guild.owner:
        return
    elif message.author == bot.user:
        await asyncio.sleep(120)
        await message.delete()
        return
    elif message.author.bot:
        return
    else:
        if message.content.startswith("http://") or message.content.startswith("https://"):
            c.execute("SELECT filters FROM link_filters WHERE channel_id = ?", (message.channel.id,))
            row = c.fetchone()
            if row:
                filters = row[0].split(';')
                if link_checker(message):
                    await message.delete()
                    await message.channel.send(f"*В этом канале доступны только* `{filters}`, *Другое не разрешено XD*")
                    return
        else:
            c.execute("SELECT filters FROM text_filters WHERE channel_id = ?", (message.channel.id,))
            row = c.fetchone()
            if row:
                text_filters = row[0].split(';')
                if text_checker(message):
                    await message.delete()
                    await message.channel.send(f"*В этом канале доступны только* `{text_filters}`, *Другое не разрешено XD*")
                    return

    await bot.process_commands(message)


@bot.slash_command(description="добавить текстовый фильтр")
async def add_text_filter(ctx, channel_id: str, filter_text: str):
    channel_id = int(channel_id)

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM text_filters WHERE channel_id = ?", (channel_id,))
    row = c.fetchone()
    if row:
        old_filters = row[0]
        new_filters = old_filters + ";" + filter_text
        c.execute("UPDATE text_filters SET filters = ? WHERE channel_id = ?", (new_filters, channel_id))
        conn.commit()
        await ctx.send('Готово')
    else:
        c.execute("INSERT INTO text_filters (channel_id, filters) VALUES (?, ?)", (channel_id, filter_text))
        conn.commit()
        await ctx.send('Готово')


@bot.slash_command(description="добавить гостевой фильтр")
async def add_guest_filter(ctx, filter_text: str):

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM guest_filters WHERE server = ?", (1,))
    row = c.fetchone()
    if row:
        old_filters = row[0]
        new_filters = old_filters + ";" + filter_text
        c.execute("UPDATE guest_filters SET filters = ? WHERE server = ?", (new_filters, 1))
        conn.commit()
        await ctx.send('Готово')
    else:
        c.execute("INSERT INTO guest_filters (server, filters) VALUES (?, ?)", (1, filter_text))
        conn.commit()
        await ctx.send('Готово')


@bot.slash_command(description="добавить гостевые роли")
async def add_guest_roles(ctx, role: disnake.Role):

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("INSERT INTO roles (role) VALUES (?)", (role.id,))
    conn.commit()
    await ctx.send('Готово')


@bot.slash_command(description="удалить гостевые роли")
async def delete_guest_roles(ctx, role: disnake.Role):

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT * FROM roles WHERE role=?", (role.id,))
    result = c.fetchone()

    if result:
        c.execute("DELETE FROM roles WHERE role=?", (role.id,))
        conn.commit()
        await ctx.send('Роль удалена из базы данных')
    else:
        await ctx.send('Роль не найдена в базе данных')


@bot.slash_command(description="добавить ссылку в фильтр")
async def add_link_filter(ctx, channel_id: str, filter_link: str):
    channel_id = int(channel_id)

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM link_filters WHERE channel_id = ?", (channel_id,))
    row = c.fetchone()
    if row:
        old_filters = row[0]
        new_filters = old_filters + ";" + filter_link
        c.execute("UPDATE link_filters SET filters = ? WHERE channel_id = ?", (new_filters, channel_id))
        conn.commit()
        await ctx.send('Готово')
    else:
        c.execute("INSERT INTO link_filters (channel_id, filters) VALUES (?, ?)", (channel_id, filter_link))
        conn.commit()
        await ctx.send('Готово')


@bot.slash_command(description="удалить текстовый фильтр (выбор)")
async def delete_filter(ctx, channel_id: str, filters: str):
    channel_id = int(channel_id)

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM text_filters WHERE channel_id = ?", (channel_id,))
    row = c.fetchone()
    if row:
        text_filters = row[0].split(';')
        new_text_filters = [filter_word for filter_word in text_filters if filter_word not in filters.split(';')]
        new_text_filters_str = ';'.join(new_text_filters)
        c.execute("UPDATE text_filters SET filters = ? WHERE channel_id = ?", (new_text_filters_str, channel_id))
        conn.commit()

        await ctx.send('Готово')
    else:
        await ctx.send('Фильтров для этого канала и не было')


@bot.slash_command(description="удалить гостевой фильтр (выбор)")
async def delete_guest_filter(ctx, filters: str):

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM guest_filters WHERE server = ?", (1,))
    row = c.fetchone()
    if row:
        text_filters = row[0].split(';')
        new_text_filters = [filter_word for filter_word in text_filters if filter_word not in filters.split(';')]
        new_text_filters_str = ';'.join(new_text_filters)
        c.execute("UPDATE guest_filters SET filters = ? WHERE server = ?", (new_text_filters_str, 1))
        conn.commit()

        await ctx.send('Готово')
    else:
        await ctx.send('Фильтров и не было')


@bot.slash_command(description="удалить фильтр ссылок (выбор)")
async def delete_link_filter(ctx, channel_id: str, filters: str):
    channel_id = int(channel_id)

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("SELECT filters FROM link_filters WHERE channel_id = ?", (channel_id,))
    row = c.fetchone()
    if row:
        link_filters = row[0].split(';')
        new_link_filters = [filter_link for filter_link in link_filters if filter_link not in filters.split(';')]
        new_link_filters_str = ';'.join(new_link_filters)
        c.execute("UPDATE link_filters SET filters = ? WHERE channel_id = ?", (new_link_filters_str, channel_id))
        conn.commit()

        await ctx.send('Готово')
    else:
        await ctx.send('Фильтров для этого канала и не было')


@bot.slash_command(description="удалить все фильтры для канала")
async def delete_all_filters(ctx, channel_id: str):
    channel_id = int(channel_id)

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("DELETE FROM text_filters WHERE channel_id = ?", (channel_id,))
    c.execute("DELETE FROM link_filters WHERE channel_id = ?", (channel_id,))
    conn.commit()

    await ctx.send('Готово')


@bot.slash_command(description="удалить все фильтры гостей")
async def delete_all_guest_filters(ctx):

    if ctx.author != ctx.guild.owner:
        await ctx.send('Команда только для создателя')
        return

    c.execute("DELETE FROM guest_filters WHERE server= ?", (1,))
    conn.commit()

    await ctx.send('Готово')


bot.run(os.getenv('TOKEN'))
