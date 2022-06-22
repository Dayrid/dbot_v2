import discord
import random
from discord.ext import commands
import config
class Pic(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def rodich(self, ctx):
		a = ['Секс машина на связи', 'Уфимский джигит смотрит на тебя', 'Этого парня боялись даже чеченцы..', 'Два гея переглядываются']
		rodich =['https://i.imgur.com/h77sRpH.jpg',
			'https://i.imgur.com/Q4I0Zlq.jpg',
			'https://i.imgur.com/QBsqRxC.jpg',
			'https://i.imgur.com/BJ27u5p.jpg',
			'https://i.imgur.com/LUMjheX.jpg',
			'https://i.imgur.com/Zh0qf2H.jpg',
			'https://i.imgur.com/jYPl59E.jpg',
			'https://i.imgur.com/3dkxqBI.jpg',
			'https://i.imgur.com/slJhrsl.jpg',
			'https://i.imgur.com/EniOq5Z.jpg',
			'https://i.imgur.com/5E0saYN.jpg',
			'https://i.imgur.com/t6hmkhm.jpg',
			'https://i.imgur.com/kPdZBbr.jpg',
			'https://i.imgur.com/uX9aYoG.jpg',
			'https://i.imgur.com/OPa40TA.jpg',
			'https://i.imgur.com/lkFXnL0.jpg',
			'https://i.imgur.com/FAvJRgy.jpg',
			'https://i.imgur.com/aWzgYXG.jpg',
			'https://i.imgur.com/AqplUOu.jpg',
			'https://i.imgur.com/bGunsBP.jpg',
			'https://i.imgur.com/SZWA5oF.jpg',
			'https://i.imgur.com/pXpcMw8.jpg']
		embed = discord.Embed(title=random.choice(a))
		embed.set_image(url=random.choice(rodich))
		embed.set_footer(text="d_bot")
		await ctx.send(embed=embed)
		config.wlog('rodich', ctx)

def setup(bot):
	bot.add_cog(Pic(bot))