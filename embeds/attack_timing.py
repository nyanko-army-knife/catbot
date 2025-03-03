from dataclasses import dataclass
from typing import override

import discord

import commons.models as models
from catbot.embeds.embed import Embeddable


@dataclass
class AttackBreakup(models.AttackBreakup, Embeddable):
	@override
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		pass
