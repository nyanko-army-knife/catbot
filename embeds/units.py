from discord.ext import commands

from commons import models, idx
from commons.models import Rarity, UnlockMethod, Duration
from .entity import Entity
from .. import utils as utils_
from ..utils import emoji_by_name, Embed


class Form:
	@staticmethod
	def embed_in(self: models.Form, embed: Embed) -> Embed:
		trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in self.traits]
		ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait.name}') for ptrait in self.ptraits]
		mult_emojis = [emoji_by_name(f'mult_{mult}') for mult in self.mults]
		embed.add_field( value=t'[**Cost:** {self.cost:,}]  [**Cooldown:** {max(self.cooldown, Duration(60)):,}]',
										)
		Entity.embed_in(self, embed)
		if trait_emojis or ptrait_emojis:
			v = "".join(mult_emojis) + " vs. " + "".join(trait_emojis)
			if ptrait_emojis: v += " | " + "".join(ptrait_emojis)
			embed.add_field(value=t"**Targets:**\n{v}")
		return embed


class Cat:
	@classmethod
	async def convert(cls, ctx: commands.Context, argument: str) -> Cat:
		return idx.units.get(int(argument))

	@staticmethod
	def embed_in(self: models.Cat, embed: Embed) -> Embed:
		embed.add_field(value=f"[**Rarity:** {Rarity(self.rarity).label}]  [**Unlock Method:** {UnlockMethod(self.unlock_method).label}]")

		max_level_base, max_level_catseyes, max_boost = self.max_level
		embed.add_field(value=f"[**Max Level**: {max_level_base}(->{max_level_catseyes}) + {max_boost}]")

		if self.tf_level > 0:
			txt = f"level: {self.tf_level}"
			if self.tf_xp:
				txt += f" | XP: {self.tf_xp:,}"
			if self.tf_reqs:
				txt += "\n"
				reqtext = []
				for req in self.tf_reqs:
					reqtext += [f"{emoji_by_name(utils_.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(value=f"**True Form**\n{txt}")

		if self.uf_level > 0:
			txt = f"level: {self.uf_level}"
			if self.uf_xp:
				txt += f" | XP: {self.uf_xp:,}"
			if self.uf_reqs:
				txt += "\n"
				reqtext = []
				for req in self.uf_reqs:
					reqtext += [f"{emoji_by_name(utils_.item_icons[req[0]])}x{req[1]}"]
				txt += " | ".join(reqtext)
			embed.add_field(value="**Ultra Form**\n"+txt)
		return embed
