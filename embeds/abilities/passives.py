import discord
from typing_extensions import override

from ..embed import Embeddable
import commons.models.abilities as abilities

class Passives(abilities.Passives, Embeddable):
	def __init__(self, passives: abilities.Passives):
		super().__init__(**vars(passives))

	@override
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		if self.immunities:
			embed.add_field(name="Immunities", value='immune to ' + ', '.join(x.to for x in self.immunities), inline=False)
		if self.resists:
			embed.add_field(name="Resistances", value='resists ' + ', '.join(f"{x.to} [{x.amt}]" for x in self.resists),
											inline=False)
		if self.defensives:
			embed.add_field(name="Defensives", value='\n'.join(str(x) for x in self.defensives), inline=False)
		if self.offensives:
			embed.add_field(name="Offensives", value='\n'.join(str(x) for x in self.offensives), inline=False)
		return embed
