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

conn.commit()


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")


@bot.event
async def on_message(message):
    if message.author == message.guild.owner:
        return
    if message.author == bot.user:
        await asyncio.sleep(120)
        await message.delete()
        return

    c.execute("SELECT filters FROM link_filters WHERE channel_id = ?", (message.channel.id,))
    row = c.fetchone()
    if row:
        filters = row[0].split(';')
        if message.content.startswith("http://") or message.content.startswith("https://"):
            flag = True
            for word in filters:
                if word == message.content.split('/')[2]:
                    flag = False
                    return
            if flag:
                await message.delete()
                await message.channel.send(f"*В этом канале доступны только* `{filters}`, *Другое не разрешено XD*")
                return

    c.execute("SELECT filters FROM text_filters WHERE channel_id = ?", (message.channel.id,))
    row = c.fetchone()
    if row:
        text_filters = row[0].split(';')
        flag = True
        if message.content.split(' ')[0] in text_filters:
            flag = False
            return
        if flag:
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


bot.run(os.getenv('TOKEN'))
