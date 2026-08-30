import json
import os
from datetime import datetime as dt

import discord
import msgspec.json
import requests
from discord.ext import commands

from catbot import embeds, utils
from catbot.utils import render
from commons import idx
from commons.models import GachaSchedule, datespan, SaleSchedule
from commons.models import ItemSchedule
from commons.utils import msg

with open("data/custom/events.json") as fl:
	custom_events = json.load(fl)

SERIES = {
	1: 'S',
	2: 'C',
	4: 'EX',
	6: 'T',
	7: 'V',
	9: 'N',
	11: 'R',
	12: 'M',
	16: 'D',
	24: 'A',
	25: 'H',
	27: 'CA',
	33: 'L',
	36: 'SR',
}


def get_stage_name(i: int) -> str:
	match i // 1000:
		case 8 | 9:
			return 'Mission: '
		case 5:
			return 'Gamatoto'
		case _:
			try:
				if nm := custom_events["events"].get(str(i)):
					return nm
				elif nm := custom_events["series"].get(str(i // 1000)):
					return nm
				else:
					return idx.categories[SERIES[i // 1_000]].maps[i % 1000].name
			except AttributeError, IndexError, KeyError:
				return f'Unknown - {i}'


class EventCog(commands.Cog):
	qualified_name = "events"

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
	)
	async def schedule_gacha(self, ctx):
		def try_get_name(id_) -> str:
			gcha = idx.gacha.get(id_)
			return "" if gcha is None else gcha.series_name

		with open("data/db_en/schedule_gacha.json") as fl:
			schedules: list[GachaSchedule] = msgspec.json.decode(fl.read(), type=list[GachaSchedule])
			schedules.sort(key=lambda schedule: (schedule.time_span[0], try_get_name(schedule.gacha_id)))

		txt = t"**Gacha Schedule**\n```\n"
		for schedule in schedules:
			if (dt.now() - schedule.time_span[0]).days > 5: continue
			# if abs((dt.now() - schedule.time_span[0]).days) > 60 or abs(
			# 				(dt.now() - schedule.time_span[1]).days) > 60: continue
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
		txt += t"G : Guaranteed | I: Item (typically Lucky Ticket) | S : Step Up | U : raised uber rate\n"
		await ctx.send(render(txt))

	@commands.command(
		aliases=['vis', 'sitem'],
		description="display item schedule",
	)
	async def schedule_item(self, ctx):
		txt = t"**Item Schedule**\n```\n"
		with open("data/db_en/schedule_item.json") as fl:
			schedules: list[ItemSchedule] = msg.dec(list[ItemSchedule]).decode(fl.read())

		for schedule in schedules:
			if (dt.now() - schedule.time_span[0]).days > 5: continue  # or abs(
			# (dt.now() - schedule.time_span[1]).days) > 60: continue
			txt += t"[{datespan(schedule.time_span)}] "
			if schedule.item_id == 301:
				txt += t"Reset:: 11 roll discount\n"
			elif schedule.item_id == 302:
				txt += t"Reset:: 1 roll discount\n"
			elif 800 <= schedule.item_id < 900:
				txt += t"Sale :: {idx.sales[schedule.item_id]}\n"
			elif 900 <= schedule.item_id < 1_000 or 35_000 <= schedule.item_id < 36_000:
				txt += t"Stamp:: {idx.stamps[schedule.item_id]}\n"
			elif 11_000 <= schedule.item_id < 12_000:
				txt += t"Dojo :: {idx.categories['R'].maps[schedule.item_id % 11_000].stages[0].name}\n"
			elif 33_000 <= schedule.item_id < 34_000:
				txt += t"Event:: Labyrinth\n"
			else:
				item_name = schedule.item_id
				try:
					item_name = idx.items_by_server_id[schedule.item_id].name
				except KeyError:
					pass
				txt += t"Item :: {item_name} x {schedule.item_qty} - {schedule.message.split('<br>')[0]}\n"

		txt += t"```\n"
		await ctx.send(render(txt))

	@commands.command(
		aliases=['vss', 'ssale'],
		description="display stage schedule",
	)
	async def schedule_sale(self, ctx):
		with open("data/db_en/schedule_sale.json") as fl:
			schedules: list[SaleSchedule] = msgspec.json.decode(fl.read(), type=list[SaleSchedule])

		txt = t"**Stage Schedule**\n```\n"
		for schedule in schedules:
			if (dt.now() - schedule.time_span[0]).days > 5 or abs(
							(dt.now() - schedule.time_span[1]).days) > 60: continue
			eventnames = '|'.join(map(get_stage_name, schedule.events))
			if 'Mission' in eventnames or 'Gamatoto' in eventnames:
				continue
			txt += t"[{datespan(schedule.time_span)}] {eventnames}\n"
		txt += t"```\n"
		await ctx.send(render(txt))

	@commands.command(
		aliases=['vas', 'sall'],
		description="display stage schedule",
	)
	async def schedule_all(self, ctx):
		await ctx.invoke(self.schedule_gacha)
		await ctx.invoke(self.schedule_item)
		await ctx.invoke(self.schedule_sale)

	@commands.command(
		aliases=['vu', ],
		description="updates event data. only works for authorised users",
	)
	async def update(self, ctx):
		role_ids = set(role.id for role in ctx.author.roles)
		guild_perms = utils.permissions.get(str(ctx.guild.id))
		if not guild_perms: return
		if not (set(guild_perms["admin_roles"]) & role_ids):
			return

		await ctx.send(trigger_workflow())


def trigger_workflow():
	url = os.getenv("GITHUB_ACTION_URL", "")

	payload = {
		"ref": "main",
		"inputs": {}
	}
	headers = {
		"accept": "application/vnd.github+json",
		"x-github-api-version": "2026-03-10",
		"authorization": f"Bearer {os.getenv("GITHUB_ACCESS_TOKEN", "")}",
		"content-type": "application/json"
	}

	response = requests.post(url, json=payload, headers=headers)
	return response.json()
