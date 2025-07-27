import discord

import commons.models as models
from commons import idx


class Stage:
	@staticmethod
	def embed_in(self: models.Stage, embed: discord.Embed) -> discord.Embed:
		specs = f"length: {self.length:,} | base hp: {self.base_health:,} | enemy limit: {self.enemy_limit}"
		embed.add_field(name="specs", value=specs, inline=False)
		misc = []
		if self.no_continues: misc.append("no continues")
		if self.boss_shield: misc.append("has boss shield")
		if misc: embed.add_field(name="misc", value=", ".join(misc), inline=False)

		for schematic in self.schematics:
			header = (f"{'★' if schematic.is_boss else ''} "
								f"{idx.enemies.get(schematic.enemy_id).name} "
								f"({schematic.mag_str})")
			spawn_str = []
			if schematic.quantity != 1: spawn_str += [f"x {schematic.qty_str}"]
			if schematic.spawn_hp < 100: spawn_str += [f"{schematic.spawn_hp}%"]
			if schematic.score > 0: spawn_str += [f"@{schematic.score}"]
			if schematic.kill_count == 0 and (
							schematic.spawn_hp == 100 or (schematic.start > 1 and schematic.is_start_after_hp)):
				spawn_str += [f"{schematic.start:,}f"]
			if schematic.quantity == 0 or schematic.quantity > 1: spawn_str += [f"⟳ {schematic.respawn_str}"]
			if schematic.kill_count > 0: spawn_str += [f"💀 {schematic.kill_count}"]

			embed.add_field(
				name=header,
				value=' | '.join(spawn_str),
				inline=True
			)
		return embed
