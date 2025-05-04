import discord
from discord.ext import commands

from catbot import embeds
from commons import idx


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
	async def stage(self, ctx, *args):
		target = " ".join(args)
		stg = embeds.Stage(idx.stages.lookup(target))
		map_ = idx.categories[stg.id_[0]].maps[stg.id_[1]]

		embed = discord.Embed(colour=discord.Colour.yellow(), title=f"{stg.name} - {map_.name} [{stg.id_str}]")
		stg.embed_in(embed)
		await ctx.send(embed=embed)
