import discord

from catbot.embeds.embed import Embeddable
from catbot.embeds.entity import Entity
from commons import models
from commons.models import Rarity, UnlockMethod

from .. import utils
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


class Cat(models.Cat, Embeddable):
	form_base: Form = None
	form_evolved: Form = None
	form_true: Form = None
	form_ultra: Form = None

	def __init__(self, cat: models.Cat):
		super().__init__(**vars(cat))

	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		embed.add_field(name="Rarity - Unlock Method",
										value=f"{Rarity(self.rarity).label} - {UnlockMethod(self.unlock_method).label}")

		max_level_base, max_level_catseyes, max_boost = self.max_level
		embed.add_field(name="Max Level", value=f"{max_level_base}(->{max_level_catseyes}) + {max_boost}")

		if self.tf_level > 0:
			txt = f"level: {self.tf_level}"
			if self.tf_xp:
				txt += f" | XP: {self.tf_xp:,}"
			if self.tf_reqs:
				txt += "\n"
				reqtext = []
				for req in self.tf_reqs:
					reqtext += [f"{emoji_by_name(utils.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(name="True Form", value=txt, inline=False)

		if self.uf_level > 0:
			txt = f"level: {self.uf_level}"
			if self.uf_xp:
				txt += f" | XP: {self.uf_xp:,}"
			if self.uf_reqs:
				txt += "\n"
				reqtext = []
				for req in self.uf_reqs:
					reqtext += [f"{emoji_by_name(utils.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(name="Ultra Form", value=txt, inline=False)
		return embed
