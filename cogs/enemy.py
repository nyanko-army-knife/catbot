import typing

import discord
from discord.ext import commands

from catbot import embeds
from catbot.utils import Embed
from commons import idx


class ESFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	enemy: embeds.Enemy = commands.flag(name='name', description="Enemy Name", positional=True, default='')
	mag: typing.Tuple[int, ...] = commands.flag(name='mag', aliases=['m'], default=(100, 100), max_args=1,
																							description="Magnification (HP, Atk)")


class EnemyCog(commands.Cog):
	qualified_name = "enemies"

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=['es'],
		description="display stats of enemy",
		help=";es bakoo\n"
				 ";es blogger\n"
				 ";es baron seal -m 10000 1000\n"
	)
	async def enemy(self, ctx, *, flags: ESFlags):
		enem = flags.enemy
		enem = enem.to_mag(*flags.mag[:2])

		embed = Embed(accent_colour=discord.Colour.red()).add_title(f"{enem.name} [{enem.id_}]", subtitle=f"{flags.mag}%")
		embeds.Enemy.embed_in(enem, embed)

		try:
			fl_id = f'{enem.id_:03}'
			upload_file = discord.File(f'data/img/enemy/{fl_id}.png', filename=f'{fl_id}.png')
			embed.add_thumbnail(upload_file)
			await ctx.send(file=upload_file, view=embed.render())
		except:
			await ctx.send(view=embed.render())

	@commands.command(
		aliases=['efind', 'ef'],
		description="finds closest matches to enemy name",
		help=';cfind bakoo\n'
	)
	async def enemy_find(self, ctx, *args):
		target = " ".join(args)
		is_quick, lookups = idx.enemies.lookup_debug(target)

		finds = [f"{x.name}: {x.score:0.02f}%" for x in lookups]

		embed = discord.Embed(colour=discord.Colour.dark_blue(), title=f"Searching enemy name {target}")
		embed.add_field(name="quick?", value=is_quick, inline=False)
		embed.add_field(name="closest finds", value="\n".join(finds), inline=False)
		await ctx.send(embed=embed)
