from collections import defaultdict
from itertools import zip_longest
import json
from discord.ui import TextDisplay
from catbot.embeds.enemy import Enemy
from catbot.utils import Embed, setup_icons
import catbot.utils
from serde.json import from_json
import pytest

TEST_ENEMIES = [
	(
		'Naala',
		'{ "name": "Ultima Beast Naala", "description": [ "A sacred primordial being, known as the ", "most ancient among all forest creatures.", "Calls down lightning to test trespassers.", "Those who survive are deemed worthy to live." ], "drop": 4500, "health": 3000000, "damage": 30000, "area_targeting": true, "breakup": { "hit_0": { "use_ability": true, "damage": 30000, "separate_range": [ 1, 200 ], "foreswing": 40 }, "hit_1": { "use_ability": true, "damage": 15000, "separate_range": [ 200, 200 ], "foreswing": 60 }, "hit_2": { "use_ability": true, "damage": 15000, "separate_range": [ 400, 200 ], "foreswing": 80 }, "backswing": 0, "cooldown": 23 }, "knockbacks": 3, "speed": 32, "standing_range": 400, "traits": "Relic", "pseudotraits": "Behemoth", "immunities": [ "Surge" ], "freeze": { "chance": 100, "duration": 90 }, "curse": { "chance": 100, "duration": 300 } }',
		['[**Drop:** 17,775]', '[**HP:** 3,000,000]  [**KB Count:** 3]  [**Atk:** 60,000]  [**DPS:** 17,647.06]', '**Timings:**\n ↑40f: **__30000__** [1~201]\n ↑20f: **__15000__** [200~400]\n ↑20f: **__15000__** [400~600]\n ↓0f / ⏲22f\n', '[**Range:** 400]  [**Area?:** True]  [**Speed:** 16]', '**Abilities:**\n— 100% chance to freeze for 90f\n— 100% chance to curse for 10.00s\n', '**Passives:**\n— immune to surge \n', '**Traits:** <:trait_relic:0><:ptrait_behemoth:0>']
	),
	(
		'Gigahaniwan',
		'{ "name": "Gigahaniwan", "description": [ "Massive haniwa excavated from an ancient", "lab and used as a weapon of war. Scrambled", "genome has given it Immunity to Curses and a", "raft of Wave attacks that inflict negative status." ], "drop": 3450, "health": 1000000, "damage": 5000, "area_targeting": true, "breakup": { "hit_0": { "use_ability": true, "damage": 5000, "foreswing": 44 }, "backswing": 0, "cooldown": 0 }, "knockbacks": 1, "speed": 10, "standing_range": 350, "traits": "Relic", "pseudotraits": "Colossus", "immunities": ["Curse"], "slow": { "chance": 30, "duration": 90 }, "freeze": { "chance": 30, "duration": 90 }, "weaken": { "chance": 30, "duration": 90, "to": 50 }, "knockback": { "chance": 30 }, "curse": { "chance": 100, "duration": 90 }, "wave": { "chance": 100, "level": 4, "mini": false } }',
		['[**Drop:** 13,628]', '[**HP:** 1,000,000]  [**KB Count:** 1]  [**Atk:** 5,000]  [**DPS:** 3,409.09]', '[**Timings**: ↑44f / ↓0f / ⏲0f]', '[**Range:** 350]  [**Area?:** True]  [**Speed:** 5]', '**Abilities:**\n— 100% chance to create a level 4 wave\n— 30% chance to slow for 90f\n— 30% chance to freeze for 90f\n— 30% chance to knockback\n— 30% chance to weaken to 50% for 90f\n— 100% chance to curse for 90f\n', '**Passives:**\n— immune to curse \n', '**Traits:** <:trait_relic:0><:ptrait_colossus:0>']
	),
	(
		'Variety Bears',
		'{ "name": "Bears Be Back", "description": [], "drop": 1000, "health": 50000, "damage": 400, "area_targeting": true, "breakup": { "hit_0": { "use_ability": true, "damage": 400, "foreswing": 15 }, "hit_1": { "use_ability": true, "damage": 400, "foreswing": 30 }, "hit_2": { "use_ability": true, "damage": 400, "foreswing": 60 }, "backswing": 0, "cooldown": 0 }, "knockbacks": 3, "speed": 60, "standing_range": 420, "traits": "Red | Floating | Dark | Angel | Alien | Zombie", "slow": { "chance": 33, "duration": 90 }, "freeze": { "chance": 33, "duration": 90 }, "weaken": { "chance": 33, "duration": 90, "to": 50 }, "warp": { "chance": 21, "distance": [ 2000, 2000 ], "duration": 30 }, "knockback": { "chance": 21 } }',
		['[**Drop:** 3,950]', '[**HP:** 50,000]  [**KB Count:** 3]  [**Atk:** 1,200]  [**DPS:** 600.00]', '**Timings:**\n ↑15f: **__400__**\n ↑15f: **__400__**\n ↑30f: **__400__**\n ↓0f / ⏲0f\n', '[**Range:** 420]  [**Area?:** True]  [**Speed:** 30]', '**Abilities:**\n— 33% chance to slow for 90f\n— 33% chance to freeze for 90f\n— 21% chance to knockback\n— 33% chance to weaken to 50% for 90f\n— 21% chance to warp for 30f over 500\n', '**Traits:** <:trait_red:0><:trait_floating:0><:trait_dark:0><:trait_angel:0><:trait_alien:0><:trait_zombie:0>']
	)
]

@pytest.fixture(autouse=True)
def init():
	catbot.utils.emojis = defaultdict(lambda: "0")

def test_enemy_embed(subtests: pytest.Subtests):
	for name, inp, out in TEST_ENEMIES:
		with subtests.test(msg=name):
			enemy = from_json(Enemy, inp)
			embed = Embed()
			o = enemy.to_mag(100).embed_in(embed)
			for field, expected in zip_longest(o.fields, out):
				assert isinstance(field, TextDisplay)
				assert field.content == expected
