import discord
from asyncio import run_coroutine_threadsafe
from discord.ext import commands
from discord.utils import get


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.buff = []

    @commands.command(brief='Check latency of the bot.')
    async def ping(self, ctx):  # Проверка задержки в ms
        latency = self.bot.latency
        latency //= 1e-3
        latency = latency + ((latency // 1e-5) % 100) / 100  # Сложные(нет) математические формулы для красивого вида
        await ctx.message.delete()
        await ctx.send(f'`{latency}ms`')


def setup(bot):
    bot.add_cog(Core(bot))
