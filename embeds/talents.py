from typing import override

import discord

import commons.models.talents.effect as effect
from catbot.embeds.embed import Embeddable


class Talents(list[effect.Talent], Embeddable):
	@override
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		for talent in self:
			np_cost = sum(talent.np_curve)
			embed.add_field(name=talent.name + (" [+]" if talent.is_ultra else "") +
													 (
														 f" ({talent.np_curve[0]}~{np_cost}NP)" if talent.max_level > 1 else f" ({talent.np_curve[0]}NP)"),
											value=f"{talent.text}\n", inline=False)
		return embed
