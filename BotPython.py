import discord
import nest_asyncio
import pymysql
import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

nest_asyncio.apply()
db = pymysql.connect(host=os.environ.get("MYSQL_IP"), port=3306, user=os.environ.get("MYSQL_USER"),
                     password=os.environ.get("MYSQL_PASSWORD"), database=os.environ.get("MYSQL_DB"))
sql = db.cursor()
sql.execute("USE bot_db;")
bot = commands.Bot(command_prefix='>')
initial_extensions = [
    'cogs.chat',
    'cogs.music',
    'cogs.radio',
    'cogs.core',
    'cogs.pic',
    'cogs.booru',
    'cogs.games',
    'cogs.listen',
]
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
    bot.remove_command('help')


@bot.event  # Событие за запуск бота
async def on_ready():
    print(f'Logged on as {bot.user}!\n{bot.user} is connected to the following guild:')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="anime | >help")  # Статус "смотрит anime"
    )


@bot.event
async def on_error(event, *args, **kwargs):  # Запись ошибок в лог
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@bot.command()
async def help(ctx):
    embed1 = (discord.Embed(title='Помощь[1]', description="**`Команды для чата:`**", color=0x3498db)
              .add_field(name='>clear кол-во', value='Чистит чат на определенное количество сообщений.')
              .add_field(name='>clear_him кто кол-во', value='Чистит сообщения определенного человека в нужном кол-ве.')
              .add_field(name='>mute кто время причина',
                         value='Мутит игрока на определенное кол-во времени(пример: 60s).')
              .add_field(name='>kick кто причина', value='Кикает нужного человека с сервера с указанием причины.')
              .add_field(name='>ban кто причина', value='Банит нужного человека с указанием причины.')
              .add_field(name='>unban кто-то', value='Снимает бан с нужного человека + причина.')
              .add_field(name='`Команды для музыки:`', value='Примечание: если бот завис - просто пропишите >skip',
                         inline=False)
              .add_field(name='>play песня/ссылка',
                         value='Бот может играть песни по названию или по ссылке на Youtube.')
              .add_field(name='>pause', value='Останавливает/продолжает воспроизведение песни.')
              .add_field(name='>skip', value='Пропускает песню, играющую в данный момент.')
              .add_field(name='>remove число', value='Удаляет песню из очереди по ее номеру.')
              .add_field(name='`Команды для ВКонтакте:`',
                         value='Примечание: некоторые команды не совсем стабильны, отправляйте только то, что тут описано.',
                         inline=False)
              .add_field(name='>vk albums [ваш id]', value='Предоставляет список ваших альбомов в вк с их id.')
              .add_field(name='>vk play [id альбома] [кол-во песен]',
                         value='Играет определенное количество песен с альбома(Альбом должен быть создан '
                               'исключительно вами)')
              .add_field(name='`Команды для радио:`',
                         value='Примечание: радио в дискорде часто зависает, пропишите >radio_stop если бот завис.',
                         inline=False)
              .add_field(name='>radio ссылка', value='Бот воспроизводит радио по *прямой ссылке* на поток.')
              .add_field(name='>radio_stop', value='Останавливает воспроизведение текущего радио и выходит с канала.'))
    await ctx.send(embed=embed1, delete_after=300.0)
    embed2 = (discord.Embed(title='Помощь[2]', color=0x3498db)
              .add_field(name='`Команды для картинок:`',
                         value='Поддерживаемые сайты: [danbooru](https://danbooru.donmai.us), [konachan]('
                               'https://konachan.net), [safebooru](https://safebooru.org), [yande.re]('
                               'https://yande.re), [gelbooru](https://gelbooru.com), [rule34](https://rule34.xxx).',
                         inline=False)
              .add_field(name='В поле сайт надо указать одну букву сайта d/k/s/y.',
                         value='Пример >b d kitsune - выведет арт на площадке Danbooru по тэгу kitsune')
              .add_field(name='>b сайт тэги', value='Ищет арт по данному тэгу.')
              .add_field(name='>bs сайт количество(макс 20) тэги', value='Ищет несколько артов по данному тэгу.')
              .add_field(name='>r34 тэги', value='Ищет один арт с платформы Rule34.')
              .add_field(name='>r34_many кол-во(макс 20) тэги', value='Ищет ищет несколько артов с платформы Rule34.')
              .add_field(name='>list', value='Выводит самые частые тэги (если несколько, то писать через пробел).')
              .add_field(name='`Команды для игр:`',
                         value='Примечание: некоторые команды не совсем стабильны, отправляйте только то, что тут '
                               'описано.',
                         inline=False)
              .add_field(name='>rr add/play',
                         value='Игра русская рулетка, для включения вас в игру пропишите >rr add, для начала - >rr '
                               'start')
              .add_field(name='>flip', value='Кидает монетку.')
              .add_field(name='>dice', value='Бросает игральные кости.')
              .add_field(name='>knb камень/ножницы/бумага',
                         value='Бот играет с вами в КНБ. Пропишите свой вариант и наслаждайтесь.')
              )
    await ctx.send(embed=embed2, delete_after=300.0)
    # config.wlog('help', ctx)


bot.run(os.getenv("DISCORD_TOKEN"))
