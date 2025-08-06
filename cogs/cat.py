import discord
from discord.ext import commands

import catbot.utils as utils
from catbot import embeds
from catbot.utils import DoubleDefault
from commons import idx
from commons.models import Cat


# gets cat and implied form ID from form name
def get_cat(form_name: str) -> tuple[Cat, int, float]:
	cat_id, form_id = -1, -1
	match_score: float = -1
	try:  # try to look up by form ID
		c_id, f_id, *_ = map(int, form_name.split("-"))
		_ = idx.units[c_id][f_id]
		cat_id, form_id = c_id, f_id
	except (IndexError, ValueError):
		form, match_score = idx.forms.lookup_with_score(form_name)
		cat_id = form.id_[0]
		if match_score > 80:
			form_id = form.id_[1]

	return idx.units.get(cat_id), form_id, match_score


class CatIDConverter(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str) -> Cat:
		return idx.units.get(int(argument))


class CSFlags(utils.ArgparseConverter):
	form_name: str = commands.flag(name='name', positional=True, description="unit name", default="")
	cat: CatIDConverter = commands.flag(name='id', default=None,
																			description="ID of unit, unit name is ignored when this is provided")
	level: utils.ForceInt = commands.flag(name='level', aliases=['lvl', 'lv', 'l'], default=50, max_args=1,
																				description="unit level")
	to_form: int = commands.flag(name='form', aliases=['f'], default=-1, max_args=1,
															 description="Unit Form (0 = first, 1 = evolved, 2 = true, 3 = ultra)")
	talents: list[int] = commands.flag(name='talents', aliases=['t'], default=DoubleDefault([], [-1]),
																		 description="Talents, send -1 to max all")
	verbose: bool = commands.flag(name='verbose', aliases=['v'], default=False, description="verbose (display summon)")


class CIFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	form_name: str = commands.flag(name='name', positional=True, description="unit name", default="")


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
	async def catstats(self, ctx: discord.ext.commands.Context, *, flags: CSFlags):
		form_id: int = -1
		if flags.cat:
			cat_, confidence = flags.cat, 100.0
		elif flags.form_name:
			cat_, form_id, confidence = get_cat(flags.form_name)
		else:
			raise ValueError("No form or cat provided")

		if flags.to_form >= 0:
			form_id = flags.to_form

		if confidence > 90 or flags.to_form >= 0:
			form, level = cat_.form_to_level(form_id, flags.level, upcast=True)
		else:
			form, level = cat_.form_to_level(form_id, flags.level)

		if flags.talents:
			talents = idx.talents[cat_.id_]
			levels = [10] * 10 if flags.talents == [-1] else flags.talents
			for t, talent_level in zip(talents, levels):
				if talent_level > 0:
					form = t.apply_level_to(talent_level, form)

		embed = discord.Embed(colour=discord.Colour.green(),
													title=f"{form.name} [{form.id_[0]}-{form.id_[1]}] (Lv. {level})")
		embeds.Form.embed_in(form, embed)

		fl_id = f"{form.id_[0]:03}_{form.id_[1]}"
		embed.set_thumbnail(url=f"attachment://{fl_id}.png")

		try:
			upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
		except FileNotFoundError:
			upload_file = None

		await ctx.send(file=upload_file, embed=embed)

		if embed.footer.text:
			spirit = await CatIDConverter().convert(ctx, ''.join(x for x in embed.footer.text if x.isnumeric()))
			flags.cat, flags.to_form = spirit, 0
			await ctx.invoke(self.catstats, flags=flags)

	@commands.command(
		aliases=['ci'],
		description="display info of cat",
		help=";ci Lasvoss\n"
	)
	async def catinfo(self, ctx: discord.ext.commands.Context, *, flags: CIFlags):
		cat_, form_id, confidence = get_cat(flags.form_name)

		embed = discord.Embed(colour=discord.Colour.green(), title=f"{cat_[-1].name} [{cat_.id_}]")
		embed = embeds.Cat.embed_in(cat_, embed)

		fl_id = f"{cat_.id_:03}_{cat_[-1].id_[1]}"
		embed.set_thumbnail(url=f"attachment://{fl_id}.png")
		try:
			upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
			await ctx.send(file=upload_file, embed=embed)
		except FileNotFoundError:
			await ctx.send(embed=embed)

	@commands.command(
		aliases=['comboname', 'cc'],
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

		embed = discord.Embed(colour=discord.Colour.greyple(),
													title=f"Talents of {form.name} [{form.id_[0]}-{form.id_[1]}]")
		embeds.Talents.embed_in(idx.talents[form.id_[0]], embed)

		await ctx.send(embed=embed)

	@commands.command(
		aliases=['cfind', 'cf'],
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
