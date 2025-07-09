import json
from datetime import datetime as dt

import discord
from discord.ext import commands

from catbot import embeds
from commons import idx
from commons.models import GachaSchedule, datespan
from commons.models.lookup import object_hook_ability


class EventCog(commands.Cog):
	qualified_name = "enemies"

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=['vg'],
		description="display gacha",
		help=";gacha E039\n"
	)
	async def gacha(self, ctx, *target):
		gacha = idx.gacha[target[0]]
		title = f"Gacha {gacha.code}{' (inactive)' if (gacha.category != 'N' and not gacha.enabled) else ''}"
		embed = discord.Embed(colour=discord.Colour.dark_green(), title=title)
		embeds.Gacha(gacha).embed_in(embed)
		await ctx.send(embed=embed)

	@commands.command(
		aliases=['vgs', 'sgacha'],
		description="display gacha schedule",
		help=";gacha E039\n"
	)
	async def schedule_gacha(self, ctx):
		txt = "**Gacha Schedule**\n```\n"
		with open("data/db/schedule_gacha.json") as fl:
			schedules: list[GachaSchedule] = json.load(fl, object_hook=object_hook_ability)
		for schedule in schedules:
			if (dt.now() - schedule.time_span[0]).days > 60: continue
			gacha = idx.gacha.get(schedule.gacha_id)
			txt += f"{datespan(schedule.time_span)} ({schedule.gacha_id}) {gacha.series_name}"
			if schedule.modifiers:
				txt += f" [{'|'.join(schedule.modifiers)}]"
			if gacha.extras:
				txt += f" [{'|'.join(gacha.extras)}]"
			txt += "\n"
		txt += "```\n"
		txt += "G : Guaranteed | GR : Grandon | N : Neneko Gang | R : Reinforcement | P : Platinum Shard | S : Step Up\n"
		await ctx.send(txt)
