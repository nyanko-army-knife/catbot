import discord
from discord.ext import commands

from commons import idx
from commons.models import enemy
from .entity import Entity
from ..utils import emoji_by_name, Embed


class Enemy:
	@classmethod
	async def convert(cls, ctx: commands.Context, argument: str) -> Enemy:
		if argument.isnumeric():
			return idx.enemies.get(int(argument))
		else:
			return idx.enemies.lookup(argument)

	@staticmethod
	def embed_in(self: enemy.Enemy, embed: Embed) -> discord.Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in self.ptraits]
		embed.add_field(name="Drop", value=f'{self.drop * 3.95:.0,f}', inline=True)
		Entity.embed_in(self, embed)
		if trait_emojis or ptrait_emojis:
			embed.add_field(name="Traits", value="".join(trait_emojis + ptrait_emojis) + "\n", inline=True)
		return embed
