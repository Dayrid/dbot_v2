import discord
import urllib
import urllib.request
import pybooru
import random
import rule34
import asyncio
import pygelbooru
import urllib.request
import config

from random import choice
from pybooru import Danbooru
from pybooru import Moebooru
from discord.ext import commands
from discord import Embed
from asyncio import run_coroutine_threadsafe
from pygelbooru import Gelbooru


class Booru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bdict = {'d': 'Danbooru', 's': 'Safebooru', 'k': 'Konachan', 'g': 'Gelbooru', 'y': 'Yande.re'}
        proxy_support = urllib.request.ProxyHandler({'http': 'http://QF0LSiJZzn:jZjvC0aQsE@45.149.133.125:54885'})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

    def search(self, tags, source, count=1):
        links = []
        if source == 'Danbooru':
            client = Danbooru('danbooru', username='Dayrid', api_key='bQyM59Sbs9GubAA7MTTt5bMg')
        elif source == 'Konachan':
            client = Moebooru('konachan', username='Dayrid', hash_string='j8tbWVay9qVbD7QYDGsz8A')
        elif source == 'Safebooru':
            client = Danbooru('safebooru', username='Dayrid', api_key='bQyM59Sbs9GubAA7MTTt5bMg')
        elif source == 'Yande.re':
            client = Moebooru('yandere', username='Dayrid', hash_string='uFVWIB7MLA56e0-evxZLtQ')
        if not client.post_list(tags=tags):
            return []
        posts = client.post_list(tags=tags, page=random.randint(1, 20), limit=40)
        while not posts:
            posts = client.post_list(tags=tags, page=random.randint(1, 20), limit=40)
        if count == 1:
            chosen = choice(posts)
            try:
                url = chosen['file_url']
            except:
                url = choice(posts)['file_url']
            return url
        else:
            for post in posts:
                try:
                    links.append(post['file_url'])
                except:
                    continue
            for link in links:
                if link.endswith(('.mp4', '.webm')):
                    links.remove(link)
            while len(links) > count:
                links.remove(choice(links))
            return links

    def get_r34(self, tags: str):
        ex_tags = '-yaoi -solo_male -male_only -futa -fart -animal_genitalia -multiple_boys -comic -male/male ' \
                  '-hyper_ass '
        tags += ex_tags
        links = []
        client = rule34.Sync()
        images = client.getImages(tags)
        if images == None:
            return None
        images = random.sample(images, 100)
        for image in images:
            if image.file_url.endswith(('.mp4', 'webm')) is False:
                links.append(image.file_url)
        url = choice(links)
        return url

    async def gbooru(self, tags: list, count=1):
        links = []
        ex_tags = ['yaoi', 'futa']
        client = Gelbooru(api_key='de94347255be18a2338908c905b3c0a002f377b684b768405d9218a87b16ac26', user_id='609451')
        if not await client.search_posts(tags=tags.split(' ')):
            return
        posts = await client.search_posts(tags=tags.split(' '), exclude_tags=ex_tags, limit=40,
                                          page=random.randint(1, 20))
        while posts == []:
            posts = await client.search_posts(tags=tags.split(' '), exclude_tags=ex_tags, limit=40,
                                              page=random.randint(1, 20))
        for post in posts:
            try:
                links.append(post.file_url)
            except:
                continue
        for link in links:
            if link.endswith(('.mp4', '.webm')):
                links.remove(link)
        if count == 1:
            url = choice(links)
            return url
        else:
            while len(links) > count:
                links.remove(choice(links))
        return links

    @commands.command()
    async def b(self, ctx, source: str, *, tag: str):
        try:
            source = self.bdict[source]
        except:
            return
        config.wlog('b', ctx)
        if source == 'Gelbooru':
            URL = str(await self.gbooru(tag))
            if not URL:
                await ctx.send('```' + 'Неизвестный тэг' + '```')
                return
        else:
            URL = self.search(tag, source, 1)
            if not URL:
                await ctx.send('```' + 'Неизвестный тэг' + '```')
                return
            while URL.endswith(('.mp4', '.webm')) is True:
                URL = self.search(tag, source, 1)
        embed = Embed()
        embed.add_field(name='Заказчик', value=ctx.author.mention)
        embed.add_field(name='Тэги', value=tag)
        embed.add_field(name='Источник', value=source)
        print(URL)
        embed.set_image(url=URL)
        embed.set_footer(text=f"d_bot")
        await ctx.send(embed=embed)

    @commands.command()
    async def bs(self, ctx, source: str, count: int, *, tag: str):
        try:
            source = self.bdict[source]
        except:
            return
        config.wlog('bs', ctx)
        if source == 'Gelbooru':
            URLS = await self.gbooru(tag, count)
            if URLS == []:
                await ctx.send('```' + 'Неизвестный тэг' + '```')
                return
        else:
            URLS = self.search(tag, source, count)
            if URLS == []:
                await ctx.send('```' + 'Неизвестный тэг' + '```')
                return
        for link in URLS:
            embed = Embed()
            embed.add_field(name='Заказчик', value=ctx.author.mention)
            embed.add_field(name='Тэги', value=tag)
            embed.add_field(name='Источник', value=source)
            embed.set_image(url=link)
            embed.set_footer(text=f"d_bot")
            await ctx.send(embed=embed)

    @commands.command()
    async def r34(self, ctx, *, tag):
        config.wlog('r34', ctx)
        URL = self.get_r34(tag)
        if URL is None:
            await ctx.send('```' + 'Неизвестный тэг' + '```')
            return
        embed = Embed()
        embed.add_field(name='Заказчик', value=ctx.author.mention)
        embed.add_field(name='Тэги', value=tag)
        embed.add_field(name='Источник', value='Rule34')
        embed.set_image(url=URL)
        embed.set_footer(text=f"d_bot")
        await ctx.send(embed=embed)

    @commands.command()
    async def r34s(self, ctx, count=1, *, tag):
        config.wlog('r34s', ctx)
        if self.get_r34(tag) is None:
            await ctx.send('```' + 'Неизвестный тэг' + '```')
            return
        for _ in range(count):
            URL = self.get_r34(tag)
            embed = Embed()
            embed.add_field(name='Заказчик', value=ctx.author.mention)
            embed.add_field(name='Тэги', value=tag)
            embed.add_field(name='Источник', value='Rule34')
            embed.set_image(url=URL)
            embed.set_footer(text=f"d_bot")
            await ctx.send(embed=embed)

    @commands.command()
    async def tag_list(self, ctx):
        config.wlog('list', ctx)
        embed = (Embed(title='Самые частые тэги',
                       description='Примечание: каких-то тэгов нет на определенных сайтах, если в запросе бот ничего не выдаст - поменяйте тэг.')
                 .add_field(name='animal_ears', value='Все ушастые целиком')
                 .add_field(name='ass', value='Жопки.')
                 .add_field(name='blue_eyes', value='Синие глаза(вместо blue может быть любой другой цвет на англ.)')
                 .add_field(name='bikini', value='Бикини')
                 .add_field(name='catgirl', value='Кошкодевочки')
                 .add_field(name='furry', value='Надеюсь ты это не будешь использовать..')
                 .add_field(name='loli', value='Ну ты понял')
                 .add_field(name='milf/mature', value='Любителям милф и дамочек по-старше')
                 .add_field(name='neko', value='Обычные коты')
                 .add_field(name='oni', value='Демоны в яп. мифологии')
                 .add_field(name='solo', value='Одиночный арт')
                 .add_field(name='short_hair/long_hair', value='Короткие/длинные волосы')
                 .add_field(name='swimsuit', value='Купальник')
                 .add_field(name='thick_thighs', value='Пухлые ляжки')
                 .add_field(name='thighhighs', value='Чулочки.')
                 .add_field(name='underwear', value='Нижнее белье')
                 )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Booru(bot))
