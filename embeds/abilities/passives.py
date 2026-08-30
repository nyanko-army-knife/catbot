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
			v += t"— immune to {', '.join(x.to for x in self.immunities)} \n"
		if self.resists:
			v += t"— resists to {', '.join(f"{y.to} [{y.amt}%]" for y in self.resists)} \n"
		if self.defensives:
			v += reduce(add, (t"— {x}\n" for x in self.defensives))
		if self.offensives:
			v += reduce(add, (t"— {x}\n" for x in self.offensives))
		if v.interpolations:
			embed.add_field(value=t"**Passives:**\n{v}")

		for offensive in self.offensives:
			if isinstance(offensive, abilities.Conjure):
				embed.set_footer(content=f"this unit has a summon: {offensive.spirit_id}")
		return embed
