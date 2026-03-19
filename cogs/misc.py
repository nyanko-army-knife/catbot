import discord
from discord.ext import commands

import random

hi = [
    "Hi!",
    "Hello!",
    "hi bro",
    "What",
    "I'm dracobot",
    "mizli > balrog",
    "Could not run command.",
    "You have to wait for 0.1sec more to use this command!"
]

class MiscCog(commands.Cog):
    qualified_name = "miscellaneous"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['sayhi'],
        description="say hi to dracobot :D"
    )
    async def say_hi(self, ctx: discord.ext.commands.Context):
        await ctx.send(random.choice(hi))
