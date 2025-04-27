import discord
from typing_extensions import override

import commons.models.abilities as abilities

from ..embed import Embeddable


class Passives(abilities.Passives, Embeddable):
	def __init__(self, passives: abilities.Passives):
		super().__init__(**vars(passives))

	@override
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		v = ""
		if self.immunities:
			v += '— immune to ' + ', '.join(x.to for x in self.immunities) + '\n'
		if self.resists:
			v += '— resists ' + ', '.join(f"{y.to} [{y.amt}%]" for y in self.resists) + '\n'
		if self.defensives:
			v += '\n'.join("— " + str(x) for x in self.defensives) + '\n'
		if self.offensives:
			v += '\n'.join("— " + str(x) for x in self.offensives) + '\n'
		if v:
			embed.add_field(name='Passives', value=v.rstrip("\n"), inline=False)

		for offensive in self.offensives:
			if isinstance(offensive, abilities.Conjure):
				embed.set_footer(text=f"this unit has a summon: {offensive.spirit_id}")
		return embed
