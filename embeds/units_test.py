from collections import defaultdict
from itertools import zip_longest
import json
from discord.ui import TextDisplay
from catbot.embeds.units import Cat, Form
from catbot.utils import Embed, setup_icons
import catbot.utils
from serde.json import from_json
import pytest

TEST_CATS = [
	(
		'Eraser Cat',
		'{ "rarity": "Normal", "base_form": { "name": "Tank Cat", "description": [ "Acts as a shield with the great health.", "Their Area attacks are strong enough to move a pebble." ], "health": 400, "damage": 2, "area_targeting": true, "cooldown": 120, "cost": 150, "breakup": { "hit_0": { "use_ability": false, "damage": 2, "foreswing": 8 }, "backswing": 0, "cooldown": 30 }, "knockbacks": 1, "speed": 16, "standing_range": 110, "ld_range": [ 0, 0 ] }, "evolved_form": { "name": "Wall Cat", "description": [ "Rigid defense, now with corners.", "Their Area attacks are strong enough to move a small rock." ], "health": 400, "damage": 2, "area_targeting": true, "cooldown": 120, "cost": 150, "breakup": { "hit_0": { "use_ability": false, "damage": 2, "foreswing": 8 }, "backswing": 0, "cooldown": 30 }, "knockbacks": 1, "speed": 16, "standing_range": 110, "ld_range": [ 0, 0 ] }, "true_form": { "name": "Eraser Cat", "description": [ "Can take a beating thanks to elasticity.", "Really Good™ Defense.", "Their Area attacks are strong enough to move two small rocks." ], "health": 600, "damage": 4, "area_targeting": true, "cooldown": 120, "cost": 150, "breakup": { "hit_0": { "use_ability": false, "damage": 4, "foreswing": 8 }, "backswing": 0, "cooldown": 30 }, "knockbacks": 1, "speed": 16, "standing_range": 110, "ld_range": [ 0, 0 ] }, "xp_curve": [ 400, 700, 1600, 2800, 4300, 6100, 8200, 10600, 13300, 16300 ], "max_levels": [ 1, 20, 90 ], "unlock_method": "Stage" }',
		['[**Rarity:** Normal]  [**Unlock Method:** Stage]', '[**Max Level**: 1(->20) + 90]']
	)
]

TEST_FORMS = [
	(
		'Eraser Cat',
		'{ "name": "Eraser Cat", "description": [ "Can take a beating thanks to elasticity.", "Really Good™ Defense." ], "health": 600, "damage": 4, "area_targeting": true, "cooldown": 120, "cost": 150, "breakup": { "hit_0": { "use_ability": false, "damage": 4, "foreswing": 8 }, "backswing": 0, "cooldown": 30 }, "knockbacks": 1, "speed": 16, "standing_range": 110, "ld_range": [ 0, 0 ] }',
		['[**Cost:** 150]  [**Cooldown:** 60f]', '[**HP:** 16,200]  [**KB Count:** 1]  [**Atk:** 107]  [**DPS:** 86.76]', '[**Timings**: ↑8f / ↓0f / ⏲29f]', '[**Range:** 110]  [**Area?:** True]  [**Speed:** 8]']
	),
	(
		'Awakened Naala',
		'{ "name": "Awakened Naala", "description": [ "Holy beast who finds beauty amidst chaotic desire.", "Colossus/Behemoth Slayer. Strong vs Relics, " ], "health": 5000, "damage": 1680, "area_targeting": true, "cooldown": 1950, "cost": 4500, "breakup": { "hit_0": { "use_ability": true, "damage": 1680, "separate_range": [ 1, 300 ], "foreswing": 40 }, "hit_1": { "use_ability": true, "damage": 1680, "separate_range": [ 300, 200 ], "foreswing": 60 }, "hit_2": { "use_ability": true, "damage": 1680, "separate_range": [ 500, 200 ], "foreswing": 80 }, "backswing": 0, "cooldown": 46 }, "knockbacks": 2, "speed": 32, "standing_range": 300, "traits": "Relic", "pseudotraits": "Behemoth | Colossus", "immunities": [ "Curse", "Surge", "Wave" ], "mults": [ "Strong" ], "weaken": { "chance": 100, "duration": 120, "to": 50 }, "behemoth_dodge": { "chance": 5, "duration": 30 } }',
		['[**Cost:** 4,500]  [**Cooldown:** 121.20s]', '[**HP:** 135,000]  [**KB Count:** 2]  [**Atk:** 136,080]  [**DPS:** 32,659.20]', '**Timings:**\n ↑40f: **__45360__** [1~301]\n ↑20f: **__45360__** [300~500]\n ↑20f: **__45360__** [500~700]\n ↓0f / ⏲45f\n', '[**Range:** 300]  [**Area?:** True]  [**Speed:** 16]', '**Abilities:**\n— 100% chance to weaken to 50% for 120f\n', '**Passives:**\n— immune to curse, surge, wave \n— 5% chance to dodge behemoth attacks for 30f\n', '**Targets:**\n<:mult_strong:0> vs. <:trait_relic:0> | <:ptrait_behemoth:0><:ptrait_colossus:0>']
	)
]

@pytest.fixture(autouse=True)
def init():
	catbot.utils.emojis = defaultdict(lambda: "0")

def test_cat_embed(subtests: pytest.Subtests):
	for name, inp, out in TEST_CATS:
		with subtests.test(msg=name):
			cat = from_json(Cat, inp)
			embed = Embed()
			o = cat.embed_in(embed)
			for field, expected in zip_longest(o.fields, out):
				assert isinstance(field, TextDisplay)
				assert field.content == expected

def test_form_embed(subtests: pytest.Subtests):
	for name, inp, out in TEST_FORMS:
		with subtests.test(msg=name):
			form = from_json(Form, inp).to_level(50, [20,20,20,20,20,10,10,10,10,10])
			embed = Embed()
			o = form.embed_in(embed)
			for field, expected in zip_longest(o.fields, out):
				assert isinstance(field, TextDisplay)
				assert field.content == expected
