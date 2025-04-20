import discord

from commons.models import enemy
from .embed import Embeddable
from .entity import Entity
from ..utils import emoji_by_name


class Enemy(enemy.Enemy, Entity, Embeddable):
	def __init__(self, enem: enemy.Enemy):
		super().__init__(**vars(enem))

	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in self.ptraits]
		embed.add_field(name="Drop", value=f'{self.drop:,}', inline=True)
		super().embed_in(embed)
		if trait_emojis or ptrait_emojis:
			embed.add_field(name="Traits", value="".join(trait_emojis + ptrait_emojis) + "\n", inline=True)
		return embed
