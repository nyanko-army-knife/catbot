from typing import Optional
from discord import ui, AllowedMentions, ButtonStyle
import discord
import discord.ext.commands as commands

import catbot.utils as utils
from catbot import embeds
from catbot.utils import DoubleDefault, Embed
from commons import idx
from commons.models import Cat, Form
from commons.models.talents import Talent


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


class CSFlags(utils.ArgparseConverter):
	form_name: str = commands.flag(name='name', positional=True, description="unit name", default="")

	cat: embeds.Cat = commands.flag(name='id', default=None,
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


def make_embed(form: Form, cat_: Cat, level: int, talents: list[Talent], levels: list[int]) -> tuple[Embed, Optional[discord.File]]:
	name = f"{form.name} [{form.id_[0]}-{form.id_[1]}] (Lv. {level})"
	embed = utils.Embed(accent_colour=discord.Colour.green()).add_title(name, f"Rarity: {cat_.rarity.label}")

	tlnts = []
	f = "**Applied Talents:** "
	for t, talent_level in zip(talents, levels):
		if talent_level > 0 and not (level < 60 and t.is_ultra):
			form = t.apply_level_to(talent_level, form)
			tlnts += [f'{t.name} [{talent_level}]']
	if tlnts:
		embed.set_footer(content=f + ', '.join(tlnts))

	embeds.Form.embed_in(form, embed)

	fl_id = f"{form.id_[0]:03}_{form.id_[1]}"

	try:
		upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
		embed.add_thumbnail(upload_file)
	except FileNotFoundError:
		upload_file = None
	return (embed, upload_file)

class CatCog(commands.Cog):
	qualified_name = "cats"

	def __init__(self, bot):
		self.bot = bot


	@commands.command(
		aliases=['cs', 'fs'],
		description="display stats of cat",
		help=";cs Lasvoss -f 2\n"
				 ";cs Akira -f 2 -t -1\n"
	)
	async def catstats(self, ctx: commands.Context[commands.Bot], *, flags: CSFlags):
		# PARSE FLAGS
		form_id: int = -1
		talents, levels = [], []
		if isinstance(flags.cat, Cat):
			cat_, confidence = flags.cat, 100.0
		elif flags.form_name:
			cat_, form_id, confidence = get_cat(flags.form_name)
		else:
			raise ValueError("No form or cat provided")

		if flags.to_form >= 0:
			form_id = flags.to_form

		if (confidence > 90 or flags.to_form >= 0) and not flags.talents:
			form, level = cat_.form_to_level(form_id, flags.level, upcast=True)
		else:
			form, level = cat_.form_to_level(form_id, flags.level)

		if flags.talents:
			talents: list[Talent] = idx.talents[cat_.id_]
			levels = [10] * 10 if flags.talents == [-1] else flags.talents + [0] * 10

		# MAKE EMBED
		embed, upload_file = make_embed(form, cat_, level, talents, levels)
		view = embed.render()


		if confidence < 95:
			(_quick, options) = idx.forms.lookup_debug(flags.form_name)
			form_names = set(idx.forms.lookup_dict[key.name].name for key in options)
			form_names = [n for n in form_names if n != form.name]
			class Dropdown(utils.InteractionAuthMixin, discord.ui.Select):
				def __init__(self):
					options=[discord.SelectOption(label=o) for o in form_names]
					super().__init__(placeholder='wanted something else?', min_values=1, max_values=1, options=options)
				async def callback(self, interaction: discord.Interaction[commands.Bot]):
					cat_, form_id, _confidence = get_cat(self.values[0])
					embed, upload_file = make_embed(cat_.forms()[form_id], cat_, level, [], [])
					view = embed.render()
					await interaction.response.edit_message(view=view, attachments=[upload_file])  # ty: ignore[no-matching-overload]
			view.add_item(ui.ActionRow(Dropdown()))


		class FormButton(utils.InteractionAuthMixin, ui.Button):
			def __init__(self, f, c, l, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.form, self.cat_, self.level = f, c, l
			async def callback(self, interaction: discord.Interaction[commands.Bot]):
				view, upload_file = make_embed(self.cat_.form_to_level(self.form.id_[1], self.level, True)[0], self.cat_, self.level, talents, levels)
				await interaction.response.edit_message(view=view.render(), attachments=[upload_file])  # ty: ignore[no-matching-overload]
		arow = ui.ActionRow()
		for f in cat_.forms():
			if f is not None and f.id_ != form.id_:
				form_name = ["Base Form", "Evolved Form", "True Form", "Ultra Form"][f.id_[1]]
				b = FormButton(f, cat_, level, label=form_name, style=ButtonStyle.green)
				arow.add_item(b)

		class CIButton(utils.InteractionAuthMixin, ui.Button):
			async def callback(self, interaction: discord.Interaction[commands.Bot]):
				e, f = CatCog.make_ci_embed(cat_)
				await interaction.response.edit_message(view=e, attachments=[f])
		arow.add_item(CIButton(label=f"Cat Info Plate", style=ButtonStyle.blurple))
		view.add_item(arow)
		await ctx.reply(view=view,file=upload_file, silent=True, allowed_mentions=AllowedMentions.none())  # ty: ignore[no-matching-overload]

		# if embed.footer and "summon:" in embed.footer.text:
		# 	spirit = await embeds.Cat.convert(ctx, ''.join(x for x in embed.footer.text if x.isnumeric()))
		# 	flags.cat, flags.to_form = spirit, 0
		# 	await ctx.invoke(self.catstats, flags=flags)

	@staticmethod
	def make_ci_embed(cat_: Cat) -> tuple[ui.LayoutView, discord.File]:
		embed = Embed(accent_colour=discord.Colour.green()).add_title(f"{cat_[-1].name}",subtitle=f"[{cat_.id_}]")
		embed = embeds.Cat.embed_in(cat_, embed)

		fl_id = f"{cat_.id_:03}_{cat_[-1].id_[1]}"
		upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
		embed.add_thumbnail(upload_file)
		return embed.render(), upload_file


	@commands.command(
		aliases=['ci'],
		description="display info of cat",
		help=";ci Lasvoss\n"
	)
	async def catinfo(self, ctx: discord.ext.commands.Context, *, flags: CIFlags):
		cat_, form_id, confidence = get_cat(flags.form_name)
		e, f = self.make_ci_embed(cat_)
		await ctx.send(file=f, view=e)

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
