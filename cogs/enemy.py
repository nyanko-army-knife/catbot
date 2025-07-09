import typing

import discord
from discord.ext import commands

from catbot import embeds
from commons import idx


class ESFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	name: str = commands.flag(name='name', description="Enemy Name", positional=True, default='')
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
		enem = embeds.Enemy(idx.enemies.lookup(flags.name))
		enem = enem.to_mag(*flags.mag[:2])

		embed = discord.Embed(colour=discord.Colour.red(), title=f"{enem.name} [{enem.id_}] {flags.mag}%")
		enem.embed_in(embed)

		fl_id = f'{enem.id_:03}'
		upload_file = discord.File(f'data/img/enemy/{fl_id}.png', filename=f'{fl_id}.png')
		embed.set_thumbnail(url=f"attachment://{fl_id}.png")
		await ctx.send(file=upload_file, embed=embed)

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
