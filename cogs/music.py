import vk_api
import requests
import config
import os

from dotenv import load_dotenv
from discord import Embed, FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL
from asyncio import run_coroutine_threadsafe
from vk_api import audio


class Music(commands.Cog, name='Music'):
    load_dotenv()
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.message = {}
        self.id_list = {}

    @staticmethod
    def parse_duration(duration):
        result = []
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        return f'{int(h):02d}:{int(m):02d}:{int(s):02d}'

    @staticmethod
    def search(author, arg):
        with YoutubeDL(Music.YDL_OPTIONS) as ydl:
            try:
                requests.get(arg)
            except:
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
            else:
                info = ydl.extract_info(arg, download=False)

        embed = (
            Embed(title='🎵 Now playing :', description=f"[{info['title']}]({info['webpage_url']})", color=0x3498db)
            .add_field(name='Duration', value=Music.parse_duration(info['duration']))
            .add_field(name='Requested by', value=author)
            .add_field(name='Uploader', value=f"[{info['uploader']}]({info['channel_url']})")
            .add_field(name="Queue", value=f"No song queued")
            .set_thumbnail(url=info['thumbnail']))

        return {'embed': embed, 'source': info['formats'][0]['url'], 'title': info['title']}

    async def edit_message(self, ctx):
        embed = self.song_queue[ctx.guild][0]['embed']
        content = "\n".join(
            [f"({self.song_queue[ctx.guild].index(i)}) {i['title']}" for i in self.song_queue[ctx.guild][1:]]) if len(
            self.song_queue[ctx.guild]) > 1 else "No song queued"
        embed.set_field_at(index=3, name="Waiting queue :", value=content, inline=False)
        await self.message[ctx.guild].edit(embed=embed)

    def play_next(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if len(self.song_queue[ctx.guild]) > 1:
            del self.song_queue[ctx.guild][0]
            run_coroutine_threadsafe(self.edit_message(ctx), self.bot.loop)
            voice.play(FFmpegPCMAudio(self.song_queue[ctx.guild][0]['source'], **Music.FFMPEG_OPTIONS),
                       after=lambda e: self.play_next(ctx))
            voice.is_playing()
        else:
            run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
            run_coroutine_threadsafe(self.message[ctx.guild].delete(), self.bot.loop)

    @commands.command(aliases=['p'], brief='>play [url/words]')
    async def play(self, ctx, *, video: str):
        config.wlog('play', ctx)
        channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        song = Music.search(ctx.author.mention, video)

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        if not voice.is_playing():
            self.song_queue[ctx.guild] = [song]
            self.message[ctx.guild] = await ctx.send(embed=song['embed'])
            voice.play(FFmpegPCMAudio(song['source'], **Music.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            voice.is_playing()
        else:
            self.song_queue[ctx.guild].append(song)
            await self.edit_message(ctx)

    @commands.command(brief='>pause')
    async def pause(self, ctx):
        config.wlog('pause', ctx)
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await ctx.message.delete()
            if voice.is_playing():
                await ctx.send('⏸️ Music paused', delete_after=5.0)
                voice.pause()
            else:
                await ctx.send('⏯️ Music resumed', delete_after=5.0)
                voice.resume()

    @commands.command(aliases=['pass', 'next'], brief='>skip')
    async def skip(self, ctx):
        config.wlog('skip/next', ctx)
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            await ctx.message.delete()
            await ctx.send('⏭️ Music skipped', delete_after=5.0)
            voice.stop()

    @commands.command(brief='>remove')
    async def remove(self, ctx, *, num: int):
        config.wlog('remove', ctx)
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            del self.song_queue[ctx.guild][num]
            await ctx.message.delete()
            await self.edit_message(ctx)

    @commands.command(brief='>vk [album] [id]||[play] [album_id] [count]')
    async def vk(self, ctx, arg, param: int, n=None):
        config.wlog('vk', ctx)
        vk_session = vk_api.VkApi(login=os.environ.get("VK_LOGIN"), password=os.environ.get("VK_PASSWORD"),
                                  app_id=int(os.environ.get("VK_APPID")),
                                  client_secret=os.environ.get("VK_CLIENT_SECRET"),
                                  scope='audio')
        vk_session.auth()
        vkaudio = audio.VkAudio(vk_session)
        if arg == 'albums':
            self.id_list[ctx.author] = param
            albums = vkaudio.get_albums(param)
            for album in albums:
                await ctx.send(f'{album["title"]}, id: {album["id"]}')
        elif arg == 'play':
            tracks = vkaudio.get(owner_id=self.id_list[ctx.author], album_id=param)
            count = 0
            for track in tracks:
                await self.play(ctx=ctx, video=f"{track['artist']} - {track['title']}")
                count += 1
                if count > (int(n) - 1):
                    break
        else:
            await ctx.send('Wrong argument, type >ru_help/>help for help')

    @commands.command(brief='>stop')
    async def stop(self, ctx):
        config.wlog('stop', ctx)
        self.song_queue[ctx.guild].clear()
        await self.skip(ctx)
        await ctx.send('Queue is cleared.')


def setup(bot):
    bot.add_cog(Music(bot))
