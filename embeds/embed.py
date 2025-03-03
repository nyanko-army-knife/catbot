from abc import abstractmethod

import discord

class Embeddable:
	@abstractmethod
	def embed_in(self, embed: discord.Embed) -> discord.Embed:
		raise NotImplementedError