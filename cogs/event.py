from datetime import datetime as dt

import discord
import msgspec.json
from discord.ext import commands

from catbot import embeds
from catbot.utils import render
from commons import idx
from commons.models import GachaSchedule, datespan


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
		embeds.Gacha.embed_in(gacha, embed)
		await ctx.send(embed=embed)

	@commands.command(
		aliases=['vgs', 'sgacha'],
		description="display gacha schedule",
		help=";gacha E039\n"
	)
	async def schedule_gacha(self, ctx):
		txt = t"**Gacha Schedule**\n```\n"
		with open("data/db/schedule_gacha.json") as fl:
			schedules: list[GachaSchedule] = msgspec.json.decode(fl.read(), type=list[GachaSchedule])
		for schedule in schedules:
			if abs((dt.now() - schedule.time_span[0]).days) > 60 or abs(
				(dt.now() - schedule.time_span[1]).days) > 60: continue
			gacha = idx.gacha.get(schedule.gacha_id)
			if gacha is None:
				continue
			txt += t"[{datespan(schedule.time_span)}]"
			if schedule.modifiers - {'P'}:
				txt += t" [{'|'.join(schedule.modifiers - {'P'})}]"
			if gacha.extras:
				txt += t" [{'|'.join(gacha.extras)}]"
			txt += t" {gacha.series_name}\n"
		txt += t"```\n"
		txt += t"G : Guaranteed | GR : Grandon | N : Neneko Gang | R : Reinforcement | S : Step Up | U : raised uber rate\n"
		await ctx.send(render(txt))
