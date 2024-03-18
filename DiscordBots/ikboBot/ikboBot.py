import os
import disnake
import sqlite3
import requests
import time
from dotenv import load_dotenv
from random import randint
from disnake.ext import commands
from pyrogram import Client
from disnake import ApplicationCommandInteraction


load_dotenv()
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

db = sqlite3.connect('ikbo.db')
sql = db.cursor()
db.commit()

dolgi = sqlite3.connect('dolgi.db')
sql_d = dolgi.cursor()
dolgi.commit()

bot = commands.Bot(command_prefix="/", help_command=None, activity=disnake.Game(name="Режет негров"),
                   intents=disnake.Intents.all())

global ver
ver = 0
global flag
flag = True


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        server_id INT
    )""")

    sql_d.execute("""CREATE TABLE IF NOT EXISTS dolgi (
                name TEXT,
                id INT,
                subjects TEXT
            )""")

    for guild in bot.guilds:
        for member in guild.members:
            if sql.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                sql.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 1000, {guild.id})")
            if sql_d.execute(f"SELECT id FROM dolgi WHERE id = {member.id}").fetchone() is None:
                sql_d.execute(f"INSERT INTO dolgi VALUES ('{member}', {member.id}, '')")
            else:
                pass

    db.commit()
    dolgi.commit()
    print('client connected')


@bot.event
async def on_member_join(member):
    if flag:
        if sql.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 1000, {member.guild.id})")
        if sql_d.execute(f"SELECT id FROM dolgi WHERE id = {member.id}").fetchone() is None:
            sql_d.execute(f"INSERT INTO dolgi VALUES ('{member}', {member.id}, '')")
        else:
            pass
        db.commit()
        dolgi.commit()
        global role
        role = disnake.utils.get(member.guild.roles, id=1154344822195359784)
        await member.add_roles(role)
    else:
        pass


@bot.slash_command(name='off')
@commands.has_permissions(administrator=True)
async def off(ctx):
    global flag
    flag = False
    await ctx.send("done")


@bot.slash_command(name='on')
@commands.has_permissions(administrator=True)
async def on(ctx):
    global flag
    flag = True
    await ctx.send("done")


@bot.slash_command(name='yarik_gay')
async def on(ctx):
    await ctx.send("Сам ты gay")


@bot.slash_command(name='calculator')
async def calc(ctx, operation: str = commands.Param(choices=['+', '-', 'x', '÷', '^']), numb1: int = commands.Param(),
               numb2: int = commands.Param()):
    try:
        if operation == '+':
            await ctx.send(f'{numb1} + {numb2} = {numb1 + numb2}')
        if operation == '-':
            await ctx.send(f'{numb1} - {numb2} = {numb1 - numb2}')
        if operation == 'x':
            await ctx.send(f'{numb1} x {numb2} = {numb1 * numb2}')
        if operation == '÷':
            await ctx.send(f'{numb1} ÷ {numb2} = {numb1 / numb2}')
        if operation == '^':
            await ctx.send(f'{numb1} ^ {numb2} = {numb1 ** numb2}')
    except:
        await ctx.send('Ошибка, проверьте введенные данные и повторите попытку')


@bot.slash_command(name='ip_info')
async def info_by_ip(ctx, ip):
    if flag:
        response = requests.get(url=f'http://ip-api.com/json/{ip}').json()

        data = {
            '[IP]': response.get('query'),
            '[Int prov]': response.get('isp'),
            '[Org]': response.get('org'),
            '[Country]': response.get('country'),
            '[Region name]': response.get('regionName'),
            '[City]': response.get('city'),
            '[ZIP]': response.get('zip'),
            '[Lat]': response.get('lat'),
            '[Lon]': response.get('lon')
        }

        embed = disnake.Embed(
            title='IP INFO',
            description='',
            colour=0xF0C43F,
        )
        for k, v in data.items():
            print(f'{k} : {v}')
            embed.add_field(name='', value=f'{k}:{v}', inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(aliases=['balance', 'cash'])
async def balance(ctx, member: disnake.Member = None):
    if flag:
        if member is None:
            await ctx.send(embed=disnake.Embed(
                description=f"""Balance of user **{ctx.author}** is {sql.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} 💎"""
            ))

        else:
            await ctx.send(embed=disnake.Embed(
                description=f"""Balance of user **{member}** is {sql.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} 💎"""
            ))
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Помощь")
async def help(ctx):
    if flag:
        embed = disnake.Embed(
            title="Команды:",
            description="/color - сменить цвет на сервере. \n/help_games - игровые комманды. \n/coin - монеточка. \n/rock_scissors_paper - камень-ножницы-бумага. \n/balance - узнать свой баланс.",
            colour=0xF0C43F,
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description='Расписание')
async def table(inter: ApplicationCommandInteraction, date: str = commands.Param(choices=["Сегодня", "Завтра", "Текущая неделя", "Следующая неделя"])):
    await inter.response.send_message("Please wait...")

    app = Client('me_client', api_id, api_hash)

    await app.start()
    await app.send_message('mirea_table_bot', date)
    time.sleep(1)
    async for message in app.get_chat_history('mirea_table_bot', 1):
        await inter.edit_original_message(message.text)
    await app.stop()


@bot.slash_command(description='Добавить долг')
async def add_dolg(interaction: disnake.ApplicationCommandInteraction, name: disnake.Member, subject: str):
    sql_d.execute(f"SELECT subjects FROM dolgi WHERE name = ?", (str(name),))
    subject = sql_d.fetchone()[0] + ' ' + subject
    sql_d.execute(f"UPDATE dolgi SET subjects = ? WHERE name = ?", (subject, str(name)))
    await interaction.response.send_message("Добавил!")
    dolgi.commit()


@bot.slash_command(description='Удалить долг')
async def delete_dolg(interaction: disnake.ApplicationCommandInteraction, name: disnake.Member, subject: str):
    for subjects in sql_d.execute(f"SELECT subjects FROM dolgi WHERE name = ?", (str(name),)).fetchone():
        if subject in subjects:
            sql_d.execute(f"SELECT subjects FROM dolgi WHERE name = ?", (str(name),))
            subjects = sql_d.fetchone()[0]
            subjects = subjects.replace(' ' + subject, '')
            sql_d.execute(f"UPDATE dolgi SET subjects = ? WHERE name = ?", (subjects, str(name)))
            await interaction.response.send_message("Удалил!")
            dolgi.commit()
    else:
        await interaction.response.send_message("Долг не найден")


@bot.slash_command(description='Посмотреть долги')
async def check_dolg(interaction: disnake.ApplicationCommandInteraction, name: disnake.Member):
    sql_d.execute(f"SELECT subjects FROM dolgi WHERE name = ?", (str(name),))
    subjects = sql_d.fetchone()[0]
    if subjects:
        await interaction.response.send_message(f"Долги пользователя {name}:\n{subjects}")
    else:
        await interaction.response.send_message("У пользователя отсутствуют долги")


@bot.slash_command(description="Помощь по игровым командам")
async def help_games(ctx):
    if flag:
        await ctx.send(f'Чтобы сыграть в монеточку пропиши "/coin" и выбери орла или решку ')
        await ctx.send(f'Чтобы сыграть в камень-нижницы-бумагу пропиши "/rock_scissor_paper" и выбери, что хочешь ')
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Сменить свой цвет")
async def color(ctx, color: str = commands.Param(
    choices=["Cyan", "Blue", "Red", "Green", "Yellow", "Orange", "Purple", "Pink", "Black", "Grey"])):
    if flag:
        Blue = disnake.utils.get(ctx.author.guild.roles, id=1154346118075928587)
        Red = disnake.utils.get(ctx.author.guild.roles, id=1154346205623619595)
        Green = disnake.utils.get(ctx.author.guild.roles, id=1154346273219031072)
        Yellow = disnake.utils.get(ctx.author.guild.roles, id=1154346341191913592)
        Black = disnake.utils.get(ctx.author.guild.roles, id=1154346391674552410)
        Grey = disnake.utils.get(ctx.author.guild.roles, id=1154346499891798046)
        Purple = disnake.utils.get(ctx.author.guild.roles, id=1154346555340505109)
        Pink = disnake.utils.get(ctx.author.guild.roles, id=1154346617479122976)
        Orange = disnake.utils.get(ctx.author.guild.roles, id=1154346708537442344)
        Cyan = disnake.utils.get(ctx.author.guild.roles, id=1154346909629173860)
        if color == "Blue":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Blue)
        if color == "Red":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Red)
        if color == "Cyan":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Cyan)
        if color == "Green":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Green)
        if color == "Yellow":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Yellow)
        if color == "Orange":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Orange)
        if color == "Purple":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Purple)
        if color == "Pink":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Pink)
        if color == "Black":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Black)
        if color == "Grey":
            await ctx.send('done')
            await ctx.author.remove_roles(Cyan, Red, Blue, Green, Yellow, Orange, Purple, Pink, Black, Grey)
            await ctx.author.add_roles(Grey)
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Сыграть в монеточку")
async def coin(ctx, side: str = commands.Param(choices=["орел(head)", "решка(tails)"])):
    if flag:
        b = randint(1, 2)
        if (side.lower() == 'орел(head)' or side.lower() == 'орёл') and b == 1:
            embed = disnake.Embed(
                title="Выпал орёл, вы выиграли 10💎(Head, you win 10💎)",
                description="Congratz!!!",
                colour=0xF0C43F,
            )
            embed.set_image(url="https://i.ibb.co/hVrnL9F/image.png")
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash + 10 WHERE id = {}".format(ctx.author.id))
            db.commit()

        elif side.lower() == 'решка(tails)' and b == 2:
            embed = disnake.Embed(
                title="Выпала решка, вы выиграли 10💎(Tails, you win 10💎)",
                description="Congratz!!!",
                colour=0xF0C43F,
            )
            embed.set_image(url="https://i.ibb.co/tZq8GQ5/image.png")
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash + 10 WHERE id = {}".format(ctx.author.id))
            db.commit()

        elif side.lower() == 'решка(tails)' and b == 1:
            embed = disnake.Embed(
                title="Выпал орёл, вы проиграли 10💎(Head, you lose 10💎)",
                description="unlucky",
                colour=0xF0C43F,
            )
            embed.set_image(url="https://i.ibb.co/hVrnL9F/image.png")
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash - 10 WHERE id = {}".format(ctx.author.id))
            db.commit()

        elif (side.lower() == 'орел(head)' or side.lower() == 'орёл') and b == 2:
            embed = disnake.Embed(
                title="Выпала решка, вы проиграли 10💎(Tails, you lose 10💎)",
                description="unlucky",
                colour=0xF0C43F,
            )
            embed.set_image(url="https://i.ibb.co/tZq8GQ5/image.png")
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash - 10 WHERE id = {}".format(ctx.author.id))
            db.commit()
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Камень ножницы бумага")
async def rock_scissors_paper(ctx, choice: str = commands.Param(
    choices=["Ножницы(Scissors)", "Камень(Rock)", "Бумага(Paper)"])):
    if flag:
        bot_choice = randint(1, 3)

        # draw

        if bot_choice == 1 and choice == "Ножницы(Scissors)":
            embed = disnake.Embed(
                title="Ничья(Draw)",
                description="",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/2XPrHXu.jpg"),
            await ctx.send(embed=embed)

        if bot_choice == 2 and choice == "Камень(Rock)":
            embed = disnake.Embed(
                title="Ничья(Draw)",
                description="",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/ACgtTP6.jpg"),
            await ctx.send(embed=embed)

        if bot_choice == 3 and choice == "Бумага(Paper)":
            embed = disnake.Embed(
                title="Ничья(Draw)",
                description="",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/dbIX7PW.jpg"),
            await ctx.send(embed=embed)

        # win

        if bot_choice == 3 and choice == "Ножницы(Scissors)":
            embed = disnake.Embed(
                title="Вы победили и получили 20💎(You win 20💎)",
                description="подкручено",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/LPNu0yL.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
            db.commit()

        if bot_choice == 2 and choice == "Бумага(Paper)":
            embed = disnake.Embed(
                title="Вы победили и получили 20💎(You win 20💎)",
                description="подкручено",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/6ASNcKc.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
            db.commit()

        if bot_choice == 1 and choice == "Камень(Rock)":
            embed = disnake.Embed(
                title="Вы победили и получили 20💎(You win 20💎)",
                description="подкручено",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/wJPhtaF.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
            db.commit()

        # lose

        if bot_choice == 3 and choice == "Камень(Rock)":
            embed = disnake.Embed(
                title="Вы проиграли 20💎(You lose 20💎)",
                description="неповезло",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/nQijO9z.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash - 20 WHERE id = {}".format(ctx.author.id))
            db.commit()

        if bot_choice == 1 and choice == "Бумага(Paper)":
            embed = disnake.Embed(
                title="Вы проиграли 20💎(You lose 20💎)",
                description="неповезло",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/Fv679Yj.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash - 20 WHERE id = {}".format(ctx.author.id))
            db.commit()

        if bot_choice == 2 and choice == "Ножницы(Scissors)":
            embed = disnake.Embed(
                title="Вы проиграли 20💎(You lose 20💎)",
                description="неповезло",
                colour=0xf900FF,
            )
            embed.set_image(url="https://i.imgur.com/h5VuUJ1.jpg"),
            await ctx.send(embed=embed)
            sql.execute("UPDATE users SET cash = cash - 20 WHERE id = {}".format(ctx.author.id))
            db.commit()
    else:
        await ctx.send("Бот на тех.обслуживании")


bot.run(os.getenv('TOKEN'))
