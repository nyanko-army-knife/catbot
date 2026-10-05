from catbot.utils import Embed
from functools import reduce
from operator import add

import discord

import commons.models.abilities as abilities
from commons import models


class Passives:
	@staticmethod
	def embed_in(self: models.Passives, embed: Embed) -> Embed:
		v = t""
		if self.immunities:
			v += t"— immune to {', '.join(str(x) for x in self.immunities)} \n"
		if self.resistances:
			v += t"— resists {', '.join(f"{y.to} [{y.by}%]" for y in self.resistances)} \n"
		if self.defensives.items:
			v += reduce(add, (t"— {x}\n" for x in self.defensives.items))
		if self.offensives.items:
			v += reduce(add, (t"— {x}\n" for x in self.offensives.items))
		if v.interpolations:
			embed.add_field(value=t"**Passives:**\n{v}")

		for offensive in self.offensives.items:
			if isinstance(offensive, abilities.Conjure):
				embed.set_footer(content=f"this unit has a summon: {offensive.spirit_id}")
		return embed
