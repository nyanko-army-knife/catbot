import json
import os

import discord
from discord.ext import commands

import commons.idx as idx
from catbot import cogs
from catbot.help import CustomHelpCommand

idx.setup()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=';', intents=intents, help_command=CustomHelpCommand())

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


@bot.event
async def on_ready():
	await bot.add_cog(cogs.CatCog(bot))
	await bot.add_cog(cogs.EnemyCog(bot))
	await bot.add_cog(cogs.StageCog(bot))


bot.run(os.getenv("CATBOT_API_KEY"))
