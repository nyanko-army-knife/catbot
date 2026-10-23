from discord.ext import commands

from commons import models, idx
from commons.models import Rarity, UnlockMethod, Duration
from .entity import Entity
from .. import utils as utils_
from ..utils import emoji_by_name, Embed


class Form(models.Form):
	def embed_in(self: models.Form, embed: Embed) -> Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait.name.lower()}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait.name.lower()}') for ptrait in self.pseudotraits]
		mult_emojis = [emoji_by_name(f'mult_{mult}') for mult in self.mults]

		cd = t'{max(self.cooldown, Duration(60)):,}'
		if self.alternate_cooldown: cd += t'/{self.cooldown * self.alternate_cooldown // 100}'

		embed.add_field( value=t'[**Cost:** {self.cost:,}]  [**Cooldown:** {cd}]',
										)
		Entity.embed_in(self, embed)
		if trait_emojis or ptrait_emojis:
			v = "".join(mult_emojis) + " vs. " + "".join(trait_emojis)
			if ptrait_emojis: v += " | " + "".join(ptrait_emojis)
			embed.add_field(value=t"**Targets:**\n{v}")
		return embed


class Cat(models.Cat):
	@classmethod
	async def convert(cls, _ctx: commands.Context, argument: str) -> models.Cat:
		t = idx.units.get(int(argument))
		assert t is not None
		return t

	def embed_in(self: models.Cat, embed: Embed) -> Embed:
		embed.add_field(value=f"[**Rarity:** {Rarity(self.rarity).label}]  [**Unlock Method:** {UnlockMethod(self.unlock_method).label}]")

		max_level_base, max_level_catseyes, max_boost = self.max_levels
		embed.add_field(value=f"[**Max Level**: {max_level_base}(->{max_level_catseyes}) + {max_boost}]")

		if self.true_form_reqs is not None:
			txt = f"level: {self.true_form_reqs.level}"
			if self.true_form_reqs.xp:
				txt += f" | XP: {self.true_form_reqs.xp:,}"
			if self.true_form_reqs.items:
				txt += "\n"
				reqtext = []
				for req in self.true_form_reqs.items:
					reqtext += [f"{emoji_by_name(utils_.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(value=f"**True Form**\n{txt}")

		if self.ultra_form_reqs is not None:
			txt = f"level: {self.ultra_form_reqs.level}"
			if self.ultra_form_reqs.xp:
				txt += f" | XP: {self.ultra_form_reqs.xp:,}"
			if self.ultra_form_reqs.items:
				txt += "\n"
				reqtext = []
				for req in self.ultra_form_reqs.items:
					reqtext += [f"{emoji_by_name(utils_.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(value="**Ultra Form**\n"+txt)
		return embed
