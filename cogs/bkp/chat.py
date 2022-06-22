import discord
from discord import Member, User, Embed
from discord.ext import commands
from asyncio import sleep
import config
class Chat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	async def mute_handler(ctx, member, messages=False):
		for channel in ctx.guild.text_channels:
			await channel.set_permissions(member, send_messages=messages)

	@commands.command(
		brief='>clear [x] Cleas chat on x messages')
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, x: int):
		await ctx.channel.purge(limit = x+1)
		config.wlog(f'clear {x}', ctx)

	@commands.command(
		brief='>clear_him [smb] [x] Clears somebodys x messages')
	@commands.has_permissions(manage_messages=True)
	async def clear_him(self, ctx, user: Member, x: int):
		def is_user(m):
			return m.author == user
		await ctx.channel.purge(limit = x+1, check = is_user)
		config.wlog(f'clear_him {user} {x}', ctx)

	@commands.command(
		brief='>mute [member] [time] [reason]')
	@commands.has_permissions(manage_messages = True)
	async def mute(self, ctx, member: Member, time: str, *, reason: str = None):
		units = {"s": [1, 'seconds'], "m": [60, 'minutes'], "h": [3600, 'hours']}
		duration = int(time[:-1]) * units[time[-1]][0]
		time = f"{time[:-1]} {units[time[-1]][1]}"
		await self.mute_handler(ctx, member)
		embed = Embed(title=":mute: User muted", description=f'{ctx.author.mention} muted **{member}** for {time}.\nReason: {reason}', color=0xe74c3c)
		await ctx.send(embed=embed, delete_after = 60)
		await sleep(duration)
		await self.mute_handler(ctx, member, True)
		embed = Embed(color=0xe74c3c, description=f'{member.mention} has been unmuted.')
		await ctx.send(embed=embed, delete_after = 60)
		config.wlog(f'mute {member} {time} {reason}', ctx)

	@commands.command(brief='>kick [member] [reason]')
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: Member, *, reason: str = None):
		embed = Embed(title=":man_judge: User kicked", description=f'{ctx.author.mention} kicked **{member}**.\nReason: {reason}', color=0xe74c3c)
		await member.kick(reason=reason)
		await ctx.send(embed=embed, delete_after = 60)
		config.wlog('kick {member} {reason}', ctx)

	@commands.command(brief='>ban [member] [reason]')
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: Member, *, reason: str = None):
		embed = Embed(title=":man_judge: User banned :", description=f'{ctx.author.mention} banned **{member}**.\nReason: {reason}', color=0xe74c3c)
		await member.ban(reason=reason)
		await ctx.send(embed=embed, delete_after = 60)
		config.wlog(f'ban {member} {reason}', ctx)

	@commands.command(brief='>unban [member] [reason]')
	@commands.has_permissions(ban_members=True)
	async def unban(self, ctx, member: str, *, reason: str = None):
		ban_list = await ctx.guild.bans()
		if not ban_list:
			embed = Embed(title="Something went wrong:", description="No users banned", color=0xe74c3c)
			await ctx.send(embed=embed); return
		for entry in ban_list:
			if member.lower() in entry.user.name.lower():
				embed = Embed(title=":man_judge: User unbanned :", description=f'{ctx.author.mention} unbanned **{entry.user.mention}**.\nReason: {reason}', color=0xe74c3c)
				await ctx.guild.unban(entry.user, reason=reason)
				await ctx.send(embed=embed); return
		embed = Embed(title="Something went wrong:", description="No matching banned users", color=0xe74c3c)
		await ctx.send(embed=embed, delete_after = 60)
		config.wlog(f'unban {member} {reason}', ctx)
		return

def setup(bot):
	bot.add_cog(Chat(bot))