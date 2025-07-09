import itertools
from operator import attrgetter

import discord

from catbot.embeds.embed import Embeddable
from commons import idx, models


class Gacha(models.Gacha, Embeddable):
	def __init__(self, gacha: models.Gacha):
		super().__init__(**vars(gacha))

	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		embed.add_field(name="series", value=self.series_id, inline=False)
		if self.chara_id >= 0:
			embed.add_field(name="chara", value=idx.units.get(self.chara_id), inline=False)
		if self.units:
			units = sorted((idx.units.get(int(unit)+1) for unit in self.units), key=attrgetter("rarity"), reverse=True)
			for group in itertools.groupby(units, attrgetter("rarity")):
				txt, rarity = [], ""
				for unit in group[1]:
					rarity = unit.rarity
					mult = int(self.units[str(unit.id_-1)])
					txt += [f"{unit.form_base.name}" + (f"X {mult}" if mult > 1 else "")]
				embed.add_field(name=f"units - {rarity}", value=", ".join(txt), inline=False)
		if self.blue_orbs:
			txt = (f"{orb_id}" + (f"X {mult}" if int(mult) > 1 else "")
						 for orb_id, mult in self.blue_orbs.items())
			embed.add_field(name="orbs", value=", ".join(txt), inline=False)
		if self.items:
			txt = (f"{idx.items.get(int(item)).name}" + (f"X {mult}" if int(mult) > 1 else "")
						 for item, mult in self.items.items())
			embed.add_field(name="items", value=", ".join(txt), inline=False)
		return embed
