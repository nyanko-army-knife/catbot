from catbot.utils import Embed
from functools import reduce
from operator import add

import discord

from commons import models
from .abilities import Passives


class Entity:
	@staticmethod
	def embed_in(self: models.Entity, embed: Embed) -> Embed:
		embed.add_field(value=t"[**HP**: {self.hp:,d}]  [**KB Count:** {self.kb:,d}]  [**Atk**: {self.atk:,d}]  [**DPS:** {self.dps:,.2f}]")

		if self.breakup.hit_1 is not None:
			embed.add_field(value=t"**Timings**:\n{self.breakup}")
		else:
			embed.add_field(value=t'[**Timings**: ↑{self.breakup.hit_0.foreswing} / ↓{self.breakup.backswing} / ⏲{self.breakup.tba}]')

		display_range = t'{self.range_}'
		basehit = self.breakup.hit_0
		if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
			if basehit.range_width > 0:
				display_range += t' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
			else:
				display_range += t' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

		embed.add_field(value=t'[**Range:** {display_range}]  [**Area?:** {self.area_attack}]  [**Speed:** {self.speed}]')

		additions = t""
		if self.extensions:
			additions += reduce(add, [t"— {x}\n" for x in self.extensions])
		if self.abilities:
			additions += reduce(add, [t"— {x}\n" for x in self.abilities])
		if additions.interpolations:
			embed.add_field(value=t"**Abilities**:\n{additions}")
		if self.passives:
			Passives.embed_in(self.passives, embed)
		return embed
