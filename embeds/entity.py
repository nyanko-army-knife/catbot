import discord

from commons import models

from .abilities import Passives


class Entity:
	@staticmethod
	def embed_in(self: models.Entity, embed: discord.Embed) -> discord.Embed:
		embed.add_field(name=f"<{'Area' if self.area_attack else 'Single'}> Atk (DPS)", value=f'{self.atk} ({30 * self.atk / self.breakup.cd_effective:.2f})',
										inline=True)
		embed.add_field(name="HP - KB Count", value=f'{self.hp:,} - {self.kb}', inline=True)

		if self.breakup.hit_1 is not None:
			output = f"{self.breakup.hit_0}f"
			if self.breakup.hit_1:
				output += f" / {self.breakup.hit_1.after(self.hit_0)}f"
				if self.breakup.hit_2:
					output += f" / {self.breakup.hit_2.after(self.hit_1)}f"
			output += f" - {self.backswing}f - {self.tba}f"
			embed.add_field(name="Foreswing - Backswing - TBA", value=output, inline=True)
		else:
			embed.add_field(name="Foreswing - Backswing - TBA",
											value=f'{self.breakup.hit_0.foreswing}f - {self.breakup.backswing}f - {self.breakup.tba}f',
											inline=True)

		display_range = f'{self.range_}'
		basehit = self.breakup.hit_0
		if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
			if basehit.range_width > 0:
				display_range += f' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
			else:
				display_range += f' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

		embed.add_field(name="Range - Speed",
										value=f'{display_range} - '
													f'{self.speed}', inline=True)

		if self.extensions or self.abilities:
			embed.add_field(name="Abilities",
											value=f"{''.join(f"— {x}\n" for x in self.extensions)}"
														f"{''.join(f"— {x}\n" for x in self.abilities)}",
											inline=False)
		if self.passives:
			Passives.embed_in(self.passives, embed)
		return embed
