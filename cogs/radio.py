import discord
from asyncio import run_coroutine_threadsafe
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
import config
class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, brief='>radio [url] Plays radio with given url')
    async def radio(self, ctx, url: str):
        global player
        channel = ctx.message.author.voice.channel
        try:
            player = await channel.connect()
            player.play(FFmpegPCMAudio(url))
        except:
            pass
        if player.is_playing():
            player.stop()
            player.play(FFmpegPCMAudio(url))
        await ctx.message.delete()
        config.wlog(f'radio {url}', ctx)

    @commands.command(pass_context=True, no_pm=True, brief='Stops the radio playing')
    async def radio_stop(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if player.is_playing():
            player.stop()
        run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
        await ctx.message.delete()
        config.wlog('radio_stop', ctx)

def setup(bot):
    bot.add_cog(Radio(bot))