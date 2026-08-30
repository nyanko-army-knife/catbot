import os

import discord
from discord.ext import commands

import commons.idx as idx
from catbot import utils
from . import cogs
from .help import CustomHelpCommand

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=[';', 'p!', '!'], intents=intents, help_command=CustomHelpCommand())


@bot.check
async def auth(ctx: discord.Message):
	if isinstance(ctx.channel, discord.channel.DMChannel): return False
	role_ids = set(role.id for role in ctx.author.roles)
	user_id = ctx.author.id
	channel_id = ctx.channel.id

	guild_perms = utils.permissions.get(str(ctx.guild.id))
	if not guild_perms: return True
	return (set(guild_perms["roles"]) & role_ids) or (user_id in guild_perms["users"]) or (
					channel_id in guild_perms["channels"])


@bot.event
async def on_ready():
	await bot.add_cog(cogs.CatCog(bot))
	await bot.add_cog(cogs.EnemyCog(bot))
	await bot.add_cog(cogs.EventCog(bot))
	await bot.add_cog(cogs.StageCog(bot))


if __name__ == "__main__":
	idx.setup()
	utils.setup_perms()
	utils.setup_icons()
	bot.run(os.getenv("CATBOT_API_KEY", ""))
