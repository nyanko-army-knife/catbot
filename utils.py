import argparse
import json
import shlex
import typing
from dataclasses import dataclass
from functools import cache
from typing import Iterable, Self

from discord.ext import commands
from discord.ext.commands import Context, Converter
from discord.ext.commands._types import BotT

emojis = {}
item_icons = {}


def setup_icons():
	global emojis, item_icons
	with open("catbot/assets_cache/emojis.json") as fl:
		emojis = json.load(fl)

	with open("catbot/assets_cache/item_icons.json") as fl:
		item_icons = {int(K): V for K, V in json.load(fl).items()}


def emoji_by_name(name: str):
	return f'<:{name}:{emojis[name]}>'


@dataclass
class DoubleDefault[T]:
	first: T
	second: T


class ForceInt(int):
	def __new__(cls, *args):
		if args and isinstance(args[0], str):
			return int(''.join(x for x in args[0] if x.isnumeric()))
		return int(*args)


class ArgumentParser(argparse.ArgumentParser):
	def error(self, message):
		raise argparse.ArgumentError(None, message)


class CoalesceConst(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		if values:
			setattr(namespace, self.dest, values)
		else:
			setattr(namespace, self.dest, self.const)


class ArgparseConverter(commands.FlagConverter):
	@classmethod
	@cache
	def parser_init(cls) -> ArgumentParser:
		parser = ArgumentParser()
		for _, flag in cls.get_flags().items():
			if flag.positional:
				parser.add_argument(flag.name, type=flag.annotation, nargs="+")
				continue

			default_val = flag.default if flag.default or isinstance(flag.annotation(), Converter) else flag.annotation()
			const = None
			nargs = "?"
			annotation = flag.annotation
			if isinstance(default_val, DoubleDefault):
				default_val, const = default_val.first, default_val.second
			if isinstance(flag.annotation, Iterable):
				annotation = typing.get_args(flag.annotation)[0]
				nargs = "*"

			parser.add_argument("-" + flag.name, *("-" + x for x in flag.aliases), action=CoalesceConst,
													default=default_val, const=const, type=annotation, nargs=nargs)
		return parser

	@classmethod
	async def convert(cls, ctx: Context[BotT], argument: str) -> Self:
		parser = cls.parser_init()
		split_args = shlex.split(argument)

		toret = cls()
		try:
			# Parse the arguments from the provided string
			ns = parser.parse_args(split_args)
			for name, flag in cls.get_flags().items():
				val = vars(ns)[flag.name]
				if flag.positional:
					val = " ".join(val)
				if isinstance(flag.annotation(), Converter) and val is not None:
					val = await flag.annotation().convert(ctx, val)
				toret.__setattr__(flag.attribute, val)
			return toret
		except argparse.ArgumentError as e:
			raise commands.BadArgument(f"**Invalid arguments:**\n> {e.message}\n\n")
