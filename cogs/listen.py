import os
import discord
import pandas as pd
import pymysql

from datetime import datetime
from discord import utils
from discord.ext import commands
from dotenv import load_dotenv

import config

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

channel_id = 0
message_id = 0


class Listen(commands.Cog):
    def __init__(self, bot):
        load_dotenv()
        self.db = pymysql.connect(host=os.environ.get("MYSQL_IP"), port=3306, user=os.environ.get("MYSQL_USER"),
                                  password=os.environ.get("MYSQL_PASSWORD"), database=os.environ.get("MYSQL_DB"))
        self.sql = self.db.cursor()
        self.sql.execute("USE bot_db;")
        self.bot = bot
        self.song_queue = {}
        self.message = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.sql.execute("SELECT cid FROM `Servers` WHERE guild_id=%s", (str(guild.id)))
            res = list(self.sql.fetchone())[0]
            r = (str(guild.id), str(guild.owner_id), guild.name, guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), res)
            self.sql.execute("REPLACE INTO `Servers` (guild_id, owner_id, name, created_at, cid) VALUES (%s, %s, %s, "
                             "%s, %s)", r)
        self.db.commit()
        query = "SELECT * FROM Servers ORDER BY guild_id"
        channel_df = pd.read_sql(sql=query, con=self.db)
        print('-' * 50, '\n', channel_df)

    @commands.command()
    async def start(self, ctx):
        log = (f"Использовал команду start", str(ctx.author.id), ctx.author.name, datetime.now().strftime("%Y-%m-%d "
                                                                                                            "%H:%M:%S"),
               str(ctx.guild.id))
        self.sql.execute("INSERT INTO `Logs` (action, user_id, user_name, created_at, guild_id) VALUES (%s, %s, "
                         "%s, %s, %s)", log)
        self.sql.execute(f"SELECT cid FROM Servers WHERE guild_id = {ctx.guild.id}")
        cid = list(self.sql.fetchone())[0]
        if cid is not None and len(cid) == 18:
            await ctx.send(f'Канал уже создан', delete_after=2.0)
        else:
            ch = await ctx.guild.create_text_channel("dbot-channel", topic="Канал для музыки и различных команд")
            reaction_lst = ["⏯", "⏹", "⏭"]
            emb = discord.Embed(color=0x7b00ff)
            emb.add_field(name='Чат', value='| [Автор](https://steamcommunity.com/id/deydya/) |')
            emb.set_footer(text="Если не знаете, что делать, пишите >help")

            emb.set_image(url='http://ii.yakuji.moe/b/src/1600903499659.png')
            message = await ch.send(embed=emb)
            for reaction in reaction_lst:
                await message.add_reaction(reaction)
            await ctx.send(f'Канал создан', delete_after=2.0)
            cid = ch.id
        self.sql.execute(f"UPDATE Servers SET cid = {cid} WHERE guild_id = {ctx.guild.id}")
        self.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
        log = (f"удалил канал {channel.name}", str(entry.user.id), entry.user.name, datetime.now().strftime("%Y-%m-%d "
                                                                                                            "%H:%M:%S"),
               str(channel.guild.id))
        self.sql.execute("INSERT INTO `Logs` (action, user_id, user_name, created_at, guild_id) VALUES (%s, %s, "
                         "%s, %s, %s)", log)
        ids = [str(i.id) for i in channel.guild.text_channels]
        self.sql.execute(f"SELECT cid FROM Servers WHERE guild_id = {channel.guild.id}")
        cid = str(list(self.sql.fetchone())[0])
        if cid is not None:
            if cid not in ids:
                self.sql.execute(f"UPDATE Servers SET cid = NULL WHERE guild_id = {channel.guild.id}")
        self.db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,
                                  payload):  # Событие на добавление эмодзи, выбор категорий или стандартной роли сервера
        if payload.guild_id == 452431997139288075:  # Проверка на мой сервер (Melancholy)
            if payload.message_id == config.POST_ID:
                if payload.guild_id is None:
                    return
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                member = await (await self.bot.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)
                try:
                    emoji = str(payload.emoji)  # эмоджик который выбрал юзер
                    role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)
                    await member.add_roles(role)  # Добавление роли
                    print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member,
                                                                                                       role))  # Запись в лог
                except KeyError as e:
                    print('[ERROR] KeyError, no role found for ' + emoji)
                except Exception as e:
                    print(repr(e))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):  # Событие на удаление эмодзи
        if payload.guild_id == 452431997139288075:  # Проверка на мой сервер (Melancholy)
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = await (await self.bot.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)
            try:
                emoji = str(payload.emoji)  # эмоджик который выбрал юзер
                role = utils.get(message.guild.roles, id=config.ROLES[emoji])  # объект выбранной роли (если есть)

                await member.remove_roles(role)
                print('[SUCCESS] Role {1.name} has been removed for user {0.display_name}'.format(member, role))
            except KeyError as e:
                print('[ERROR] KeyError, no role found for ' + emoji)
            except Exception as e:
                print(repr(e))


def setup(bot):
    bot.add_cog(Listen(bot))
