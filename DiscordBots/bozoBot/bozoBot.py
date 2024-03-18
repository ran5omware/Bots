import os
import glob
import shutil
import disnake
import sqlite3
import requests
from dotenv import load_dotenv
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from random import randint
from icrawler.builtin import BingImageCrawler

load_dotenv()

db = sqlite3.connect('server.db')
sql = db.cursor()
db.commit()

db1 = sqlite3.connect('anime.db')
sql1 = db1.cursor()
db1.commit()

bot = commands.Bot(command_prefix="/", help_command=None, activity=disnake.Game(name="Rainbow Six: Siege 🎮"),
                   intents=disnake.Intents.all())

prices = [[0, 40, 80, 120, 160],
          [200, 250, 300, 350, 400],
          [455, 505, 555, 605, 655],
          [755, 855, 955, 1055, 1155],
          [1355, 1550, 1750, 1950, 2150],
          [2400, 2775, 3150, 3525, 3900],
          [4275, 5275, 6275, 7275, 8275],
          [9275]]

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

    sql1.execute("""CREATE TABLE IF NOT EXISTS anime(
        name TEXT,
        season INT,
        episode INT
    )""")
    db.commit()
    db1.commit()

    for guild in bot.guilds:
        for member in guild.members:
            if sql.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                sql.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 1000, {guild.id})")
            else:
                pass

    db.commit()
    print('client connected')


@bot.event
async def on_member_join(member):
    if flag:
        if sql.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 1000, {member.guild.id})")
            db.commit()
        else:
            pass
        role_guest = disnake.utils.get(member.guild.roles, id=1099501007282647130)
        await member.add_roles(role_guest)


@bot.slash_command(name='addanime', description='команда позволяющая добавлять аниме в список')
async def addAnime(interaction: disnake.ApplicationCommandInteraction, name: str, season: int, episode: int):
    if flag:
        sql1.execute("SELECT name FROM anime")
        if sql1.fetchone() != name:
            sql1.execute("INSERT INTO anime VALUES (?, ?, ?)", (name, season, episode))
            db1.commit()
            await interaction.response.send_message("Добавил!", ephemeral=True)
        else:
            await interaction.response.send_message("Запись по этому аниме уже имеется", ephemeral=True)
    else:
        pass


@bot.slash_command(name='animelist', description='команда позволяющая вывести весь список аниме')
async def AnimeList(interaction: disnake.ApplicationCommandInteraction):
    if flag:
        messages = []
        for value in sql1.execute("SELECT * FROM anime"):
            messages.append(f"Аниме {value[0]}, Сезон {value[1]} Серия {value[2]}")

        if messages:
            await interaction.response.send_message('\n'.join(messages), ephemeral=True)
        else:
            await interaction.response.send_message("Список аниме пуст.", ephemeral=True)
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


@bot.slash_command(name='generate_photo')
async def geph(inter: ApplicationCommandInteraction, word: str, count: int):
    if flag:
        os.mkdir('./img')
        await inter.response.send_message("Please wait...")

        filters = dict(
            type='photo',
            size='large'
        )

        crawler = BingImageCrawler(storage={'root_dir': './img'})

        crawler.crawl(
            keyword=word,
            max_num=count,
            overwrite=True,
            filters=filters,
            file_idx_offset='auto'
        )

        path = '/home/bozoadmin/bozo/bozovenv/img/'
        for filename in glob.glob(path + '*'):
            await inter.followup.send(file=disnake.File(filename))
        await inter.edit_original_message(content="Thank you for waiting!")
        shutil.rmtree('./img')


@bot.slash_command(name='calculator')
async def calc(ctx, operation: str = commands.Param(choices=['+', '-', 'x', '÷', '^', 'div', 'mod']),
               numb1: int = commands.Param(), numb2: int = commands.Param()):
    try:
        if operation == '+':
            await ctx.send(f'{numb1} + {numb2} = {numb1 + numb2}')
        if operation == '-':
            await ctx.send(f'{numb1} - {numb2} = {numb1 - numb2}')
        if operation == 'x':
            await ctx.send(f'{numb1} x {numb2} = {numb1 * numb2}')
        if operation == '÷':
            await ctx.send(f'{numb1} ÷ {numb2} = {numb1 / numb2}')
        if operation == 'div':
            await ctx.send(f'{numb1} div {numb2} = {numb1 // numb2}')
        if operation == 'mod':
            await ctx.send(f'{numb1} mod {numb2} = {numb1 % numb2}')
        if operation == '^':
            await ctx.send(f'{numb1} ^ {numb2} = {numb1 ** numb2}')
    except Exception as e:
        await ctx.send(f'{e}, проверьте введенные данные и повторите попытку')


@bot.slash_command(name='ip_info')
@commands.has_permissions(administrator=True)
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
            description="/price - узнать цену буста. \n/price_help - как пользоваться командой price. \n/funpay - ссылка на funpay. \n/help_games - игровые комманды.",
            colour=0xF0C43F,
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Помощь по игровым командам")
async def help_games(ctx):
    if flag:
        await ctx.send(f'Чтобы сыграть в монеточку пропиши "/coin **орел/решка**" ')
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Помощь по команде price")
async def price_help(ctx):
    if flag:
        await ctx.send(
            f' /price "изначальное звание (1-5)" "необходимое звание (1-5)" "количество даваемого рп" "какое звание в прошлом сезоне" "передача аккаунта нам или игра в пати (0/1)" "shadow ban (0/1)"',
            delete_after=1800)
        await ctx.send(f' Пример запроса: /price copper 2 platinum 5 emerald 50 1 0')
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Получить ссылку на funpay")
async def funpay(ctx):
    if flag:
        await ctx.send(f'https://funpay.com/users/665767/')
    else:
        await ctx.send("Бот на тех.обслуживании")


@bot.slash_command(description="Сменить свой цвет", guild_ids=[1099379230174888037, 912371572587757599])
async def color(ctx, color: str = commands.Param(
    choices=["Cyan", "Blue", "Red", "Green", "Yellow", "Orange", "Purple", "Pink", "Black", "Grey"])):
    if flag:
        Blue = disnake.utils.get(ctx.author.guild.roles, id=1117582273013878926)
        Red = disnake.utils.get(ctx.author.guild.roles, id=1117582206559338496)
        Green = disnake.utils.get(ctx.author.guild.roles, id=1117582326109569118)
        Yellow = disnake.utils.get(ctx.author.guild.roles, id=1117582391981113404)
        Black = disnake.utils.get(ctx.author.guild.roles, id=1117582549372387499)
        Grey = disnake.utils.get(ctx.author.guild.roles, id=1117582660240429177)
        Purple = disnake.utils.get(ctx.author.guild.roles, id=1117582465691824268)
        Pink = disnake.utils.get(ctx.author.guild.roles, id=1117582505218949170)
        Orange = disnake.utils.get(ctx.author.guild.roles, id=1117582425430691970)
        Cyan = disnake.utils.get(ctx.author.guild.roles, id=1118600401755844660)
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


@bot.slash_command(description="Узнать цену буста в r6")
async def price(ctx, now: str = commands.Param(
    choices=["copper", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "champion"]),
                now_n: int = commands.Param(choices=["1", "2", "3", "4", "5"]), need: str = commands.Param(
            choices=["copper", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "champion"]),
                need_n: int = commands.Param(choices=["1", "2", "3", "4", "5"]), last_season: str = commands.Param(
            choices=["copper", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "champion"]),
                rp: int = commands.Param(), party: bool = commands.Param(choices=["да", "нет"]),
                shadowban: bool = commands.Param(choices=["да", "нет"])):
    if flag:
        prices_dict = {
            'copper': prices[0],
            'bronze': prices[1],
            'silver': prices[2],
            'gold': prices[3],
            'platinum': prices[4],
            'emerald': prices[5],
            'diamond': prices[6],
            'champion': prices[7]
        }
        rank = {
            'copper': 0,
            'bronze': 1,
            'silver': 2,
            'gold': 3,
            'platinum': 4,
            'emerald': 5,
            'diamond': 6,
            'champion': 7
        }

        if now.lower() in prices_dict:
            b_index = 5 - now_n
            now_n = prices_dict[now.lower()][b_index]

        if need.lower() in prices_dict:
            d_index = 5 - need_n
            need_n = prices_dict[need.lower()][d_index]

        if rp > 70:
            if rank[last_season.lower()] < rank[need.lower()]:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.2}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.2}')
            else:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n)}')
        elif rp < 70 and rp > 45:
            if rank[last_season.lower()] < rank[need.lower()]:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.2 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.2 * 1.2}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5 * 1.2 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.2 * 1.2}')
            else:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.2}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.2}')
        elif rp < 45:
            if rank[last_season.lower()] < rank[need.lower()]:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.2 * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.5 * 1.2}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5 * 1.2 * 1.5 * 1.2}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.2 * 1.5 * 1.2}')
            else:
                if party == 1:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.5 * 1.2 * 1.5}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 2 * 1.2 * 1.5}')
                else:
                    if shadowban == 1:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.5 * 1.2 * 1.5}')
                    else:
                        await ctx.send(f'Цена: {(need_n - now_n) * 1.2 * 1.5}')
    else:
        await ctx.send("Бот на тех.обслуживании")


bot.run(os.getenv('TOKEN'))
