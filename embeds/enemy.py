from typing import Self
import discord
from discord.ext import commands

from commons import idx
from commons.models import enemy
from .entity import Entity
from ..utils import emoji_by_name, Embed


class Enemy(enemy.Enemy):
	@classmethod
	async def convert(cls, _ctx: commands.Context, argument: str) -> enemy.Enemy:
		if argument.isnumeric():
			return idx.enemies.get(int(argument))
		else:
			return idx.enemies.lookup(argument)

	@staticmethod
	def embed_in(self: enemy.Enemy, embed: Embed) -> Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in self.ptraits]
		embed.add_field(value=t'[**Drop**: {self.drop * 3.95:,.0f}]')
		Entity.embed_in(self, embed)
		if trait_emojis or ptrait_emojis:
			embed.add_field(value="**Traits:** "+"".join(trait_emojis + ptrait_emojis))
		return embed
