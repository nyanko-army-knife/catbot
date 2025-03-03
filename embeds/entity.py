from dataclasses import dataclass

import discord

from catbot.embeds.embed import Embeddable
from commons import models
from .abilities import Passives


@dataclass
class Entity(models.Entity, Embeddable):
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		embed.add_field(name="Atk", value=f'{self.atk:,}\n({30 * self.atk / self.breakup.cd_effective:.2f} DPS)',
										inline=True)
		embed.add_field(name="HP", value=f'{self.hp:,}', inline=True)
		embed.add_field(name="Spd", value=self.speed, inline=True)

		display_range = f'{self.range_}'
		basehit = self.breakup.hit_0
		if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
			if basehit.range_width > 0:
				display_range += f' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
			else:
				display_range += f' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

		embed.add_field(name="Range", value=display_range, inline=True)
		embed.add_field(name="Area?", value=self.area_attack, inline=True)
		embed.add_field(name="KB Count", value=self.kb, inline=True)

		if self.breakup.hit_1 is not None:
			embed.add_field(name="Breakup", value=str(self.breakup), inline=False)
		else:
			embed.add_field(name="Timings",
											value=f'{self.breakup.hit_0.foreswing}f/{self.breakup.backswing}f/{self.breakup.tba}f',
											inline=True)

		if self.extensions:
			embed.add_field(name="Extensions", value='\n'.join(str(x) for x in self.extensions), inline=False)
		if self.passives:
			Passives(self.passives).embed_in(embed)
		if self.abilities:
			embed.add_field(name="Actives", value='\n'.join(str(x) for x in self.abilities), inline=False)
		return embed
