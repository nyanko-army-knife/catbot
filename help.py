from typing import Any

from discord.ext import commands
from discord.ext.commands import Command, FlagConverter
from typing_extensions import override


class CustomHelpCommand(commands.DefaultHelpCommand):
	@override
	def add_command_arguments(self, command: Command[Any, ..., Any], /) -> None:
		arguments = command.clean_params.values()
		if not arguments: return None
		arg = next(iter(arguments), None)
		if not issubclass(arg.annotation, FlagConverter):
			return super().add_command_arguments(command)
		arguments = list(arg.annotation.get_flags().values())

		self.paginator.add_line(self.arguments_heading)
		max_size = self.get_max_size(arguments)  # type: ignore # not a command

		for argument in arguments:
			name = argument.name
			entry = (f'{self.indent * " "}{name:<{max_size}} '
							 f'{f'[{','.join(argument.aliases)}] ' if argument.aliases else ''} '
							 f'{argument.description or self.default_argument_description}')
			# we do not want to shorten the default value, if any.
			entry = self.shorten_text(entry)
			if argument.default is not None:
				entry += f' (default: {argument.default})'

			self.paginator.add_line(entry)
		return None
