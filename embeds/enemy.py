import discord

from commons.models import enemy

from ..utils import emoji_by_name
from .entity import Entity


class Enemy:
	@staticmethod
	def embed_in(self: enemy.Enemy, embed: discord.Embed) -> discord.Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in self.ptraits]
		embed.add_field(name="Drop", value=f'{self.drop:,}', inline=True)
		Entity.embed_in(self, embed)
		if trait_emojis or ptrait_emojis:
			embed.add_field(name="Traits", value="".join(trait_emojis + ptrait_emojis) + "\n", inline=True)
		return embed
