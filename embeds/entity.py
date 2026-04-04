from functools import reduce
from operator import add

import discord

from commons import models
from .abilities import Passives


class Entity:
	@staticmethod
	def embed_in(self: models.Entity, embed: discord.Embed) -> discord.Embed:
		embed.add_field(name="Atk (DPS)", value=f'{self.atk:,} ({30 * self.atk / self.breakup.cd_effective:,.2f})',
										inline=True)
		embed.add_field(name="HP - KB Count", value=f'{self.hp:,} - {self.kb}', inline=True)

		if self.breakup.hit_1 is not None:
			embed.add_field(name="Timings", value=self.breakup, inline=True)
		else:
			embed.add_field(name="Timings",
											value=t'↑{self.breakup.hit_0.foreswing} / ↓{self.breakup.backswing} / ⏲{self.breakup.tba}',
											inline=True)

		display_range = t'{self.range_}'
		basehit = self.breakup.hit_0
		if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
			if basehit.range_width > 0:
				display_range += t' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
			else:
				display_range += t' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

		embed.add_field(name="Range - Area? - Speed",
										value=t'{display_range} - '
													t'{self.area_attack} - '
													t'{self.speed}', inline=True)

		additions = t""
		if self.extensions:
			additions += reduce(add, [t"— {x}\n" for x in self.extensions])
		if self.abilities:
			additions += reduce(add, [t"— {x}\n" for x in self.abilities])
		if additions:
			embed.add_field(name="Abilities", value=additions, inline=False)
		if self.passives:
			Passives.embed_in(self.passives, embed)
		return embed
