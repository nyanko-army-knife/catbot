from functools import reduce
from operator import add

from catbot.utils import Embed
from commons import models
from .abilities import Passives


class Entity:
	@staticmethod
	def embed_in(self: models.Entity, embed: Embed) -> Embed:
		embed.add_field(
			value=t"[**HP:** {self.health:,d}]  [**KB Count:** {self.knockbacks:,d}]  [**Atk:** {self.damage:,d}]  [**DPS:** {self.dps:,.2f}]")

		if self.breakup.hit_1 is not None:
			embed.add_field(value=t"**Timings:**\n{self.breakup}")
		else:
			embed.add_field(
				value=t'[**Timings**: ↑{self.breakup.hit_0.foreswing} / ↓{self.breakup.backswing} / ⏲{self.breakup.tba}]')

		display_range = t'{self.standing_range}'
		# show only standing range for multi-range-hitters, and non-LD units.
		if self.breakup.hit_0.separate_range and not (self.breakup.hit_1 and self.breakup.hit_1.separate_range):
			range_start, range_width = self.breakup.hit_0.separate_range
			if range_width > 0:
				display_range += t' [{range_start}~{range_start + range_width}]'
			else:
				display_range += t' [{range_start + range_width}~{range_start}]'

		embed.add_field(
			value=t'[**Range:** {display_range}]  [**Area?:** {self.area_targeting}]  [**Speed:** {self.speed // 2}]')

		additions = t""
		if self.extensions.items:
			additions += reduce(add, [t"— {x}\n" for x in self.extensions.items])
		if self.actives.items:
			additions += reduce(add, [t"— {x}\n" for x in self.actives.items])
		if additions.interpolations:
			embed.add_field(value=t"**Abilities:**\n{additions}")
		if self.passives:
			Passives.embed_in(self.passives, embed)
		return embed
