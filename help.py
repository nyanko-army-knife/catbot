from typing import Any

import discord
from discord.ext import commands
from discord.ext.commands import Command, FlagConverter
from typing_extensions import override


class CustomHelpCommand(commands.DefaultHelpCommand):
	@override
	def add_command_arguments(self, command: Command[Any, ..., Any], /) -> None:
		"""Indents a list of command arguments after the :attr:`.arguments_heading`.

		The default implementation is the argument :attr:`~.commands.Parameter.name` indented by
		:attr:`indent` spaces, padded to ``max_size`` using :meth:`~HelpCommand.get_max_size`
		followed by the argument's :attr:`~.commands.Parameter.description` or
		:attr:`.default_argument_description` and then shortened
		to fit into the :attr:`width` and then :attr:`~.commands.Parameter.displayed_default`
		between () if one is present after that.

		.. versionadded:: 2.0

		Parameters
		-----------
		command: :class:`Command`
				The command to list the arguments for.
		"""
		arguments = command.clean_params.values()
		if not arguments:
			return
		arg = next(iter(arguments), None)
		if not issubclass(arg.annotation, FlagConverter):
			return super().add_command_arguments(command)
		arguments = list(arg.annotation.get_flags().values())

		self.paginator.add_line(self.arguments_heading)
		max_size = self.get_max_size(arguments)  # type: ignore # not a command

		get_width = discord.utils._string_width
		for argument in arguments:
			name = argument.name
			width = max_size - (get_width(name) - len(name))
			entry = f'{self.indent * " "}{name:<{width}} ' \
							f'{f'[{','.join(argument.aliases)}] ' if argument.aliases else ''}' \
							f'{argument.description or self.default_argument_description}'
			# we do not want to shorten the default value, if any.
			entry = self.shorten_text(entry)
			if argument.default is not None:
				entry += f' (default: {argument.default})'

			self.paginator.add_line(entry)
