import os
import typing

import discord
from discord.ext import commands

import commons.idx as idx
from catbot import embeds

idx.setup()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command(aliases=['comboname'])
async def combo(ctx, *args):
	target = " ".join(args)
	cmb = idx.combos.lookup(target)

	embed = discord.Embed(colour=discord.Colour.blurple(), title=f"{cmb.name} [{cmb.id_}]")
	embed.add_field(name="Effect", value=cmb.effect.name + " " + cmb.size.name, inline=False)
	embed.add_field(name="Cats", value=", ".join(idx.units[c][f].name for c, f in cmb.cats), inline=False)
	await ctx.send(embed=embed)


@bot.command(aliases=['talentsof'])
async def talent(ctx, *args):
	target = " ".join(args)
	form = idx.forms.lookup(target)
	talents = embeds.Talents(idx.talents[form.id_[0]])

	embed = discord.Embed(colour=discord.Colour.greyple(), title=f"Talents of {form.name} {form.id_}")
	talents.embed_in(embed)

	await ctx.send(embed=embed)


class ESFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	name: str = commands.flag(name='name', positional=True, default='')
	mag: typing.Tuple[int, ...] = commands.flag(name='mag', aliases=['m'], default=(100,), max_args=1)


@bot.command(aliases=['es'])
async def enemy(ctx, *, flags: ESFlags):
	enem = embeds.Enemy(idx.enemies.lookup(flags.name))
	enem = enem.apply_mag(*flags.mag[:2])

	embed = discord.Embed(colour=discord.Colour.red(), title=f"{enem.name} [{enem.id_}] {flags.mag}%")
	enem.embed_in(embed)

	fl_id = f'{enem.id_:03}'
	upload_file = discord.File(f'data/img/enemy/{fl_id}.png', filename=f'{fl_id}.png')
	embed.set_thumbnail(url=f"attachment://{fl_id}.png")
	await ctx.send(file=upload_file, embed=embed)


class CSFlags(commands.FlagConverter, delimiter=' ', prefix='-', case_insensitive=True):
	name: str = commands.flag(name='name', positional=True, default='')
	level: int = commands.flag(name='level', aliases=['l'], default=30, max_args=1)
	form: int = commands.flag(name='form', aliases=['f'], default=0, max_args=1)
	talents: typing.Tuple[int, ...] = commands.flag(name='talents', aliases=['t'], default=[])


@bot.command(aliases=['cs'])
async def cat(ctx, *, flags: CSFlags):
	form = idx.forms.lookup(flags.name)
	form = embeds.Form(idx.units[form.id_[0]].to_level(flags.level).forms()[form.id_[1]])

	embed = discord.Embed(colour=discord.Colour.green(), title=f"{form.name} [{form.id_[0]}-{form.id_[1]}] (Lv. "
																														 f"{flags.level})")
	form.embed_in(embed)
	embed.add_field(name="talents", value=flags.talents, inline=False)

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
