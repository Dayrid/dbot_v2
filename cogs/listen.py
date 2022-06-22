import discord
import asyncio
import youtube_dl
import os
import shutil
import pymysql
from discord import Guild
from discord import utils
from discord.utils import get
from discord.ext import commands
import config
import pandas as pd

channel_id = 0
message_id = 0


class Listen(commands.Cog):
    def __init__(self, bot):
        self.db = pymysql.connect(host="78.140.162.244", port=3306, user="dayrid", password='03112001jcrh',
                                  database='bot_db')
        self.sql = self.db.cursor()
        self.bot = bot
        self.song_queue = {}
        self.message = {}

    @commands.Cog.listener()
    async def on_ready(self):

        # self.sql.execute ("""CREATE TABLE IF NOT EXISTS cid (
        # server_ID BIGINT,
        # channel_ID BIGUNT
        # )""")
        # self.db.commit()
        for guild in self.bot.guilds:
            num = self.sql.execute(f"SELECT channel_id FROM channel_control WHERE server_id = {guild.id}")
            if num == 0:
                self.sql.execute(f"INSERT INTO channel_control VALUES ({guild.id}, '{guild.name}', 0)")
            else:
                pass
            self.sql.execute(f"SELECT server_name FROM channel_control WHERE server_id = {guild.id}")
            if self.sql.fetchone()[0] is None:
                self.sql.execute(
                    f"UPDATE channel_control SET server_name = '{guild.name}' WHERE server_id = {guild.id}")
            self.db.commit()

        # if self.sql.execute(f"SELECT channel_id FROM channel_control WHERE channel_id = {channel_id}").fetchone()
        # is None: self.sql.execute(f"INSERT INTO channel_control VALUES (0, {channel_id})") self.db.commit()
        query = "SELECT * FROM channel_control ORDER BY server_id"
        channel_df = pd.read_sql(sql=query, con=self.db)
        print('-' * 50, '\n', channel_df)

    @commands.command()
    async def start(self, ctx):
        config.wlog('start', ctx)
        flag = False
        self.sql.execute(f"SELECT channel_id FROM channel_control WHERE server_id = {ctx.guild.id}")
        channel_id = self.sql.fetchone()[0]
        await ctx.message.delete()
        guild = ctx.guild
        for channel in guild.channels:
            if channel.id == channel_id:
                flag = True
        if flag is False:
            await guild.create_text_channel('dbot-channel')
            await ctx.send(f'Канал создан', delete_after=2.0)
            for channel in guild.channels:
                if (channel.name == 'dbot-channel'):
                    channel_id = channel.id
                    break
            self.sql.execute(f"UPDATE channel_control SET channel_id = {channel_id} WHERE server_id = {guild.id}")
            self.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        self.sql.execute(f"SELECT channel_id FROM channel_control WHERE server_id = {channel.guild.id}")
        channel_id = self.sql.fetchone()[0]
        if (channel.id == channel_id):
            await channel.guild.create_text_channel('dbot-channel')
            for channel in channel.guild.channels:
                if (channel.name == 'dbot-channel'):
                    channel_id = channel.id
                    break
            self.sql.execute(
                f"UPDATE channel_control SET channel_id = {channel_id} WHERE server_id = {channel.guild.id}")
            self.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        global message_id
        if (channel.name == 'dbot-channel'):
            emb = discord.Embed(color=0x7b00ff)
            emb.add_field(name='Ну ты это, команды пиши', value='| [Автор](https://steamcommunity.com/id/deydya/) |')
            emb.set_footer(text="Если не знаете, что делать, пишите >help")

            emb.set_image(url='http://ii.yakuji.moe/b/src/1600903499659.png')
            message = await channel.send(embed=emb)
            message_id = message.id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,
                                  payload):  # Событие на добавление эмодзи, выбор категорий или стандартной роли сервера
        if (payload.guild_id == 452431997139288075):  # Проверка на мой сервер (Melancholy)
            if payload.message_id == config.POST_ID:
                if (payload.guild_id is None):
                    return
                guild = self.bot.get_guild(payload.guild_id)  # Получение обьекта гильдии по его ID
                try:
                    member = guild.get_member(payload.user_id)  # Получние обьекта пользователя
                    emoji = str(payload.emoji)  # эмоджик который выбрал юзер
                    role = utils.get(guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)
                    await member.add_roles(role)  # Добавление роли
                    print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member,
                                                                                                       role))  # Запись в лог
                except KeyError as e:
                    print('[ERROR] KeyError, no role found for ' + emoji)
                except Exception as e:
                    print(repr(e))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):  # Событие на удаление эмодзи
        if (payload.guild_id == 452431997139288075):  # Проверка на мой сервер (Melancholy)
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            try:
                emoji = str(payload.emoji)  # эмоджик который выбрал юзер
                role = utils.get(guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

                await member.remove_roles(role)
                print('[SUCCESS] Role {1.name} has been removed for user {0.display_name}'.format(member, role))
            except KeyError as e:
                print('[ERROR] KeyError, no role found for ' + emoji)
            except Exception as e:
                print(repr(e))


def setup(bot):
    bot.add_cog(Listen(bot))
