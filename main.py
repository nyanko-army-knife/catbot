import json
import os
import typing

import discord
from discord.ext import commands

import commons.idx as idx
from catbot import embeds
from catbot.help import CustomHelpCommand

idx.setup()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=CustomHelpCommand())

with open("catbot/assets_cache/privileges.json") as fl:
	permissions = json.load(fl)


@bot.check
async def auth(ctx: discord.Message):
	role_ids = set(role.id for role in ctx.author.roles)
	user_id = ctx.author.id
	channel_id = ctx.channel.id

	guild_perms = permissions.get(str(ctx.guild.id))
	if not guild_perms: return True
	return (set(guild_perms["roles"]) & role_ids) or (user_id in guild_perms["users"]) or (
					channel_id in guild_perms["channels"])


@bot.command(aliases=['comboname'])
async def combo(ctx, *args):
	target = " ".join(args)
	cmb = idx.combos.lookup(target)

	embed = discord.Embed(colour=discord.Colour.blurple(), title=f"{cmb.name} [{cmb.id_}]")
	embed.add_field(name="Effect", value=cmb.effect.name + " " + cmb.size.name, inline=False)
	embed.add_field(name="Cats", value=", ".join(idx.units[c][f].name for c, f in cmb.cats), inline=False)
	await ctx.send(embed=embed)


@bot.command(aliases=['talentsof', 'to'])
async def talent(ctx, *args):
	target = " ".join(args)
	form = idx.forms.lookup(target)
	talents = embeds.Talents(idx.talents[form.id_[0]])

	embed = discord.Embed(colour=discord.Colour.greyple(), title=f"Talents of {form.name} {form.id_}")
	talents.embed_in(embed)

	await ctx.send(embed=embed)


class ESFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	name: str = commands.flag(name='name', description="Enemy Name", positional=True, default='')
	mag: typing.Tuple[int, ...] = commands.flag(name='mag', aliases=['m'], default=(100, 100), max_args=1,
																							description="Magnification (HP, Atk)")


@bot.command(aliases=['es'])
async def enemy(ctx, *, flags: ESFlags):
	enem = embeds.Enemy(idx.enemies.lookup(flags.name))
	enem = enem.to_mag(*flags.mag[:2])

	embed = discord.Embed(colour=discord.Colour.red(), title=f"{enem.name} [{enem.id_}] {flags.mag}%")
	enem.embed_in(embed)

	fl_id = f'{enem.id_:03}'
	upload_file = discord.File(f'data/img/enemy/{fl_id}.png', filename=f'{fl_id}.png')
	embed.set_thumbnail(url=f"attachment://{fl_id}.png")
	await ctx.send(file=upload_file, embed=embed)


class CatIDConverter(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str):
		return idx.units.get(int(argument))


class CSFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	form: str = commands.flag(name='name', positional=True, default=None, description="Unit Name")
	cat: CatIDConverter = commands.flag(name='id', default=None,
																			description="ID of unit, unit name is ignored when this is provided")
	level: int = commands.flag(name='level', aliases=['l'], default=30, max_args=1, description="Unit Level")
	to_form: int = commands.flag(name='form', aliases=['f'], default=-1, max_args=1,
															 description="Unit Form (0 = first, 1 = evolved, 2 = true, 3 = ultra)")
	talents: typing.Tuple[int, ...] = commands.flag(name='talents', aliases=['t'], default=tuple(),
																									description="Talents, send -1 to max all")


@bot.command(aliases=['cs'])
async def cat(ctx, *, flags: CSFlags):
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
			form = t.apply_level_to(level, form)

	embed = discord.Embed(colour=discord.Colour.green(),
												title=f"{form.name} [{form.id_[0]}-{form.id_[1]}] (Lv. {flags.level})")
	embeds.Form(form).embed_in(embed)

	fl_id = f"{form.id_[0]:03}_{form.id_[1]}"
	embed.set_thumbnail(url=f"attachment://{fl_id}.png")
	upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
	await ctx.send(file=upload_file, embed=embed)


@bot.command(aliases=['si'])
async def stage(ctx, *args):
	target = " ".join(args)
	stg = embeds.Stage(idx.stages.lookup(target))
	map_ = idx.categories[stg.id_[0]].maps[stg.id_[1]]

	embed = discord.Embed(colour=discord.Colour.yellow(), title=f"{stg.name} - {map_.name} [{stg.id_str}]")
	stg.embed_in(embed)
	await ctx.send(embed=embed)


bot.run(os.getenv("CATBOT_API_KEY"))
