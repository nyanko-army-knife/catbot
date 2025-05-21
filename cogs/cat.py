import typing

import discord
from discord.ext import commands

from catbot import embeds
from commons import idx


class CatIDConverter(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str):
		return idx.units.get(int(argument))


class CSFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	form: str = commands.flag(name='name', positional=True, description="unit name", default="")
	cat: CatIDConverter = commands.flag(name='id', default=None,
																			description="ID of unit, unit name is ignored when this is provided")
	level: int = commands.flag(name='level', aliases=['l'], default=50, max_args=1, description="unit level")
	to_form: int = commands.flag(name='form', aliases=['f'], default=-1, max_args=1,
															 description="Unit Form (0 = first, 1 = evolved, 2 = true, 3 = ultra)")
	talents: typing.Tuple[int, ...] = commands.flag(name='talents', aliases=['t'], default=tuple(),
																									description="Talents, send -1 to max all")


class CatCog(commands.Cog):
	qualified_name = "cats"

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=['cs'],
		description="display stats of cat",
		help=";cs Lasvoss -f 2\n"
				 ";cs Akira -f 2 -t -1\n"
	)
	async def cat(self, ctx: discord.ext.commands.Context, *, flags: CSFlags):
		form, match_score = None, -1
		if flags.form:
			form, match_score = idx.forms.lookup_with_score(flags.form)
			cat_ = idx.units[form.id_[0]]
		elif flags.cat:
			cat_ = flags.cat
		else:
			raise ValueError("either cat ID or form should be provided")

		forms = cat_.to_level(flags.level).forms()

		if 0 <= flags.to_form < len(forms):
			form = forms[flags.to_form]
		elif flags.form and match_score > 80:
			form = forms[form.id_[-1]]
		else:
			form = forms[-1]

		if flags.talents:
			talents = idx.talents[cat_.id_]
			levels = [10] * 10 if flags.talents == (-1,) else flags.talents
			for t, level in zip(talents, levels):
				if level > 0:
					form = t.apply_level_to(level, form)

		embed = discord.Embed(colour=discord.Colour.green(),
													title=f"{form.name} [{form.id_[0]}-{form.id_[1]}] (Lv. {flags.level})")
		embeds.Form(form).embed_in(embed)

		fl_id = f"{form.id_[0]:03}_{form.id_[1]}"
		embed.set_thumbnail(url=f"attachment://{fl_id}.png")

		try:
			upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
		except FileNotFoundError:
			upload_file = None

		await ctx.send(file=upload_file, embed=embed)

		if embed.footer.text:
			spirit = await CatIDConverter().convert(ctx, ''.join(x for x in embed.footer.text if x.isnumeric()))
			flags.cat = spirit
			flags.form = None
			flags.to_form = 0
			await ctx.invoke(self.cat, flags=flags)

	@commands.command(
		aliases=['comboname'],
		description="display effect and units of combo",
		help=";combo biobone\n"
	)
	async def combo(self, ctx, *args):
		target = " ".join(args)
		cmb = idx.combos.lookup(target)

		embed = discord.Embed(colour=discord.Colour.blurple(), title=f"{cmb.name} [{cmb.id_}]")
		embed.add_field(name="Effect", value=cmb.effect.name + " " + cmb.size.name, inline=False)
		embed.add_field(name="Cats", value=", ".join(idx.units[c][f].name for c, f in cmb.cats), inline=False)
		await ctx.send(embed=embed)

	@commands.command(
		aliases=['talentsof', 'to'],
		description="list talents of cat",
		help=';to Lasvoss\n'
				 ';to dark lazer\n'
	)
	async def talent(self, ctx, *args):
		target = " ".join(args)
		form = idx.forms.lookup(target)
		talents = embeds.Talents(idx.talents[form.id_[0]])

		embed = discord.Embed(colour=discord.Colour.greyple(), title=f"Talents of {form.name} {form.id_}")
		talents.embed_in(embed)

		await ctx.send(embed=embed)

	@commands.command(
		aliases=['cfind'],
		description="finds closest matches to cat name",
		help=';cfind Lasvoss\n'
				 ';cfind dark lazer\n'
	)
	async def catfind(self, ctx, *args):
		target = " ".join(args)
		is_quick, lookups = idx.forms.lookup_debug(target)

		finds = [f"{x.name}: {x.score:0.02f}%" for x in lookups]

		embed = discord.Embed(colour=discord.Colour.dark_blue(), title=f"Searching name {target}")
		embed.add_field(name="quick?", value=is_quick, inline=False)
		embed.add_field(name="closest finds", value="\n".join(finds), inline=False)
		await ctx.send(embed=embed)
