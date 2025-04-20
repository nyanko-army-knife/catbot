import discord

from catbot.embeds.embed import Embeddable
from catbot.embeds.entity import Entity
from commons import models
from ..utils import emoji_by_name


class Form(models.Form, Entity, Embeddable):
	def __init__(self, form: models.Form):
		super().__init__(**vars(form))

	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in self.ptraits]
		mult_emojis = [emoji_by_name(f'mult_{mult}') for mult in self.mults]
		embed.add_field(name="Cost - Cooldown",
										value=f'{self.cost:,} - '
													f'{self.cooldown:,}f',
										inline=True)
		super().embed_in(embed)
		if trait_emojis or ptrait_emojis:
			v = "".join(mult_emojis) + " vs. " + "".join(trait_emojis)
			if ptrait_emojis: v += " | " + "".join(ptrait_emojis)
			embed.add_field(name="Targets", value=v, inline=True)
		return embed


class Cat(models.Cat):
	form_base: Form = None
	form_evolved: Form = None
	form_true: Form = None
	form_ultra: Form = None

	def __init__(self, cat: models.Cat):
		super().__init__(cat)

	def to_level(self, level: int) -> 'Cat':
		return super().to_level(level)

	def forms(self) -> list[Form]:
		return super().forms()
