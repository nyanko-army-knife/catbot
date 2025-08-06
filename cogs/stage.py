import itertools
import typing
from dataclasses import dataclass

import discord
from discord.ext import commands

import commons.models
from catbot import embeds
from commons import idx

CATEGORIES = {
	"A": "Gauntlet",
	"B": "Catamin",
	"H": "Enigma",
	"N": "SoL",
	"NA": "UL",
	"ND": "ZL",
	"Q": "Behemoth",
	"R": "Ranking Dojo",
	"SR": "Colloseum",
	"T": "Dojo",
	"V": "Heavenly Tower",
	"L": "Labyrinth",
}


@dataclass
class SIFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	stage: str = commands.flag(name='name', positional=True, description="unit name", default="")
	id_: typing.Tuple[str, int, int] = commands.flag(name='stage_id', aliases=['id'], description="stage ID",
																									 default=None)


class StageSelect(discord.ui.Select):
	def __init__(self, ctx, stages: list[commons.models.Stage], page_num: int):
		self.ctx: commands.Context = ctx
		self.stages = {stage.id_[-1]: stage for stage in stages}
		options = [
			discord.SelectOption(label=stage.name, value=str(stage.id_[-1]))
			for stage in stages
		]
		super().__init__(placeholder=f"page {page_num}", max_values=1, min_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		await self.ctx.invoke(self.ctx.bot.get_command("si"),
													args=SIFlags(stage="", id_=self.stages[int(self.values[0])].id_))


class MapSelect(discord.ui.Select):
	def __init__(self, ctx, maps: list[commons.models.Map], page_num: int):
		self.ctx = ctx
		self.maps = {map_.id_[-1]: map_ for map_ in maps}
		options = [
			discord.SelectOption(label=map_.name, value=str(map_.id_[-1]))
			for map_ in maps
		]
		super().__init__(placeholder=f"page {page_num}", max_values=1, min_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		stage_batches = itertools.batched(self.maps[int(self.values[0])].stages, 25)
		await interaction.response.send_message(content="choose stage", ephemeral=True, view=SelectorView(
			StageSelect(self.ctx, batch, i + 1) for i, batch in enumerate(stage_batches))
																						)


class CategorySelect(discord.ui.Select):
	def __init__(self, ctx):
		self.ctx = ctx
		options = [
			discord.SelectOption(label=cat_name, value=cat)
			for cat, cat_name in CATEGORIES.items()
		]
		super().__init__(placeholder="select category", max_values=1, min_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		map_batches = itertools.batched(idx.categories[self.values[0]].maps, 25)
		await interaction.response.send_message(content="choose map", ephemeral=True, view=SelectorView(
			MapSelect(self.ctx, batch, i + 1) for i, batch in enumerate(map_batches))
																						)


class SelectorView(discord.ui.View):
	def __init__(self, selectors, timeout=180):
		super().__init__(timeout=timeout)
		for selector in selectors:
			self.add_item(selector)


class StageCog(commands.Cog):
	qualified_name = "stages"

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=['si'],
		description="display stats of stage",
		help=";si substalker\n"
				 ";si cats in the stars\n"
	)
	async def stage(self, ctx, *, args: SIFlags):
		stg = idx.stages.lookup(args.stage)
		if args.id_ is not None:
			try:
				cat, map_, stg_ = args.id_
				stg = idx.categories[cat].maps[map_].stages[stg_]
			except KeyError:
				pass

		m_ = idx.categories[stg.id_[0]].maps[stg.id_[1]]
		embed = discord.Embed(colour=discord.Colour.yellow(), title=f"{stg.name} - {m_.name} [{stg.id_str}]")
		embeds.Stage.embed_in(stg, embed)
		await ctx.send(embed=embed)

	@commands.command(
		aliases=['sl', 'isi'],
		description="interactive stage lookup",
		help=";sl\n"
	)
	async def interactive_stage(self, ctx, *args):
		await ctx.send("stage lookup", view=SelectorView([CategorySelect(ctx)]))

	@commands.command(
		aliases=['sfind'],
		description="finds closest matches to stage name",
		help=';sfind cats in the staaars\n'
	)
	async def stage_find(self, ctx, *args):
		target = " ".join(args)
		is_quick, lookups = idx.stages.lookup_debug(target)

		finds = [f"{x.name}: {x.score:0.02f}%" for x in lookups]

		embed = discord.Embed(colour=discord.Colour.dark_blue(), title=f"Searching stage name {target}")
		embed.add_field(name="quick?", value=is_quick, inline=False)
		embed.add_field(name="closest finds", value="\n".join(finds), inline=False)
		await ctx.send(embed=embed)
