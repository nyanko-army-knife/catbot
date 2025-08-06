from typing import Any

import discord
from discord.ext import commands
from discord.ext.commands import Command
from typing_extensions import override

from catbot.utils import ArgparseConverter


class CustomHelpCommand(commands.DefaultHelpCommand):
	@override
	async def send_bot_help(self, mapping):
		embed = discord.Embed(title="Command List")
		for cog, cmds in mapping.items():
			command_signatures = [f"**{self.get_command_signature(c)}** --- {c.description}" for c in cmds if c.description]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "no category")
				embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

		channel = self.get_destination()
		await channel.send(embed=embed)

	@override
	def get_command_signature(self, command: Command):
		name = command.name
		if command.aliases:
			name += f' [/{'/'.join(command.aliases)}]'

		return name

	async def send_command_help(self, command):
		embed = discord.Embed(title=self.get_command_signature(command))
		embed.add_field(name="Description", value=command.description, inline=False)

		argtext = self.command_arguments(command)
		if argtext:
			embed.add_field(name="Arguments", value=argtext, inline=False)

		if command.help:
			embed.add_field(name="Examples", value=command.help, inline=False)

		channel = self.get_destination()
		await channel.send(embed=embed)

	def command_arguments(self, command: Command[Any, ..., Any], /) -> str:
		arguments = command.clean_params.values()
		if not arguments: return ""
		arg = next(iter(arguments), None)
		if not issubclass(arg.annotation, ArgparseConverter):
			return ""
		arguments = list(arg.annotation.get_flags().values())

		self.paginator.add_line(self.arguments_heading)
		entry = ""
		for argument in arguments:
			entry += (f'**{argument.name}** '
								f'{f'**[/{'/'.join(argument.aliases)}]** ' if argument.aliases else ''} '
								f' --- {argument.description or self.default_argument_description}')
			if argument.default is not None:
				entry += f' (default: {argument.default})'
			entry += '\n'

		return entry
