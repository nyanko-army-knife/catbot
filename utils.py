from discord import ui
import argparse
import datetime
import json
import shlex
import typing
from dataclasses import dataclass
from functools import cache
from string.templatelib import Template
from typing import Iterable, Self, Any, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context, Converter

emojis = {}
item_icons = {}


def setup_icons():
	global emojis, item_icons
	with open("catbot/assets_cache/emojis.json") as fl:
		emojis = json.load(fl)

	with open("catbot/assets_cache/item_icons.json") as fl:
		item_icons = {int(K): V for K, V in json.load(fl).items()}


permissions = {}


def setup_perms():
	global permissions
	with open("catbot/assets_cache/privileges.json") as fl:
		permissions = json.load(fl)


def emoji_by_name(name: str):
	return f'<:{name}:{emojis[name]}>'


def render(v: Template) -> str:
	out = ""
	for piece in v:
		if isinstance(piece, str):
			out += f"{piece!s}"
		else:
			if isinstance(piece.value, Template):
				out += render(piece.value)
			elif isinstance(piece.value, datetime.datetime):
				out += f"{piece.value:%b-%d}"
			else:
				try:
					out += render(piece.value.text())
				except:
					out += f"{piece.value:{piece.format_spec}}"
	return out


class Embed(ui.Container):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.footer: Optional[ui.Item] = None
		self.thumbnail: Optional[ui.Thumbnail] = None
		self.fields: list[ui.Item] = []

	def add_title(self, title: str, subtitle: str) -> Self:
		self.fields.insert(0, ui.TextDisplay(f"## {subtitle}"))
		self.fields.insert(0, ui.TextDisplay(f"## {title}"))
		return self

	def add_thumbnail(self, file: discord.File) -> Self:
		self.thumbnail = ui.Thumbnail(media=file)
		return self

	def set_footer(self, content: str) -> Self:
		self.footer = ui.TextDisplay(f"-# {content}")
		return self

	def add_field(self, value: Any) -> Self:
		out = str(value)
		if isinstance(value, Template):
			out = render(value)

		self.fields.append(ui.TextDisplay(f"{out}"))
		return self

	def render(self) -> ui.LayoutView:
		if self.thumbnail is not None:
			self.add_item(ui.Section(*self.fields[0:3], accessory=self.thumbnail))
			self.fields = self.fields[3:]
		for field in self.fields:
			self.add_item(field)
		if self.footer is not None:
			self.add_item(self.footer)
		return ui.LayoutView().add_item(self)


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
				parser.add_argument(flag.name, type=flag.annotation, nargs="*", default="")
				continue

			default_val = flag.default
			annotation = flag.annotation
			if isinstance(flag.annotation(), Converter):
				annotation = str
			const = None
			nargs = "?"
			if isinstance(default_val, DoubleDefault):
				default_val, const = default_val.first, default_val.second
			if isinstance(flag.annotation, Iterable):
				annotation = typing.get_args(flag.annotation)[0]
				nargs = "*"

			parser.add_argument("-" + flag.name, *("-" + x for x in flag.aliases), action=CoalesceConst,
													default=default_val, const=const, type=annotation, nargs=nargs)
		return parser

	@classmethod
	async def convert(cls, ctx: Context, argument: str) -> Self:
		parser = cls.parser_init()
		# clear single quotes for names like d'arkt which cause issues here
		split_args = shlex.split(argument.replace("'", ""))

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

class InteractionAuthMixin():
	async def interaction_check(self, interaction: discord.Interaction[commands.Bot]) -> bool:
		if isinstance(interaction.user, discord.User): return False
		if not isinstance(interaction.channel, discord.TextChannel): return False

		role_ids = set(role.id for role in interaction.user.roles)
		user_id = interaction.user.id
		channel_id = interaction.channel.id

		guild_perms = permissions.get(str(interaction.channel.guild.id))
		if not guild_perms: return True
		return bool(set(guild_perms["roles"]) & role_ids) or (user_id in guild_perms["users"]) or (
						channel_id in guild_perms["channels"])
