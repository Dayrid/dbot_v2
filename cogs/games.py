import discord
from asyncio import run_coroutine_threadsafe
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
import random
import config


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_queue = []
        self.gamer_stats = {}

    @commands.command(pass_context=True, no_pm=True,
                      brief='>rr add Adds you to russian rulette game.')
    async def rr(self, ctx, arg: str):
        if arg == 'add':
            if ctx.author in self.game_queue:
                await ctx.send('Ты уже в списке!😊', delete_after=10.0)
            else:
                self.game_queue.append(ctx.author)
                await ctx.send("Отлично, ты в игре!👍")
            config.wlog('add', ctx)
        elif arg == 'play':
            if self.game_queue == []:
                await ctx.send('Очередь игроков пуста, пропиши >rr add!', delete_after=10.0)
            else:
                for player in self.game_queue:
                    await ctx.send(f'Игрок {player.name} испытывает удачу!')
                    attempt = random.randint(1, 6)
                    print(f'[Russian Rulette]{player.name} rolled {attempt}!')
                    if attempt in {1, 2}:
                        await ctx.send(f'{player.name} умер🥺')
                    # await player.kick(reason = 'You lose!')
                    else:
                        await ctx.send(f'Промах! {player.name} еще живой!🔥')
                self.game_queue.clear()
            config.wlog('play', ctx)
        elif arg == 'clean':
            if self.game_queue == []:
                await ctx.message.delete()
            else:
                self.game_queue.clear()
                ctx.send('Очередь была очищена.', delete_after=10.0)
        else:
            await ctx.message.delete()
            await ctx.send('Этой команды не существует.', delete_after=10.0)

    @commands.command(pass_context=True)
    async def flip(self, ctx):
        await ctx.send('Подбрасываем монетку. Смотрим, что выпало...')
        attempt = random.randint(1, 2)
        if attempt == 1:
            await ctx.send('Выпал Орёл!')
        else:
            await ctx.send('Выпала Решка!')
        config.wlog('flip', ctx)

    @commands.command(pass_context=True)
    async def dice(self, ctx):
        await ctx.send('Подбрасываем кости...')
        attempt1 = random.randint(1, 6)
        attempt2 = random.randint(1, 6)
        if attempt2 == attempt1:
            await ctx.send('Вам повезло, вам выпал дубль!')
            await ctx.send(f'{attempt1}, {attempt2}')
        else:
            await ctx.send(f'Вам выпало: {attempt1}, {attempt2}')
        config.wlog('dice', ctx)

    @commands.command(pass_context=True)
    async def knb(self, ctx, arg):
        arg = arg.lower()
        answerlist = ['камень', 'ножницы', 'бумага']
        answer = random.choice(answerlist)
        await ctx.send(f'Вы поставили - {arg}, я - {answer}.')
        if (arg == 'камень' and answer == 'камень') or (arg == 'ножницы' and answer == 'ножницы') or (
                arg == 'бумага' and answer == 'бумага'):
            await ctx.send('Ничья!')
        elif (arg == 'камень' and answer == 'ножницы') or (arg == 'ножницы' and answer == 'бумага') or (
                arg == 'бумага' and answer == 'камень'):
            await ctx.send('Вы победили!')
        elif (arg == 'камень' and answer == 'бумага') or (arg == 'ножницы' and answer == 'камень') or (
                arg == 'бумага' and answer == 'ножницы'):
            await ctx.send('Я победил!')
        else:
            await ctx.send('Неверно задан агрумент.')
        config.wlog('knb', ctx)


def setup(bot):
    bot.add_cog(Games(bot))
