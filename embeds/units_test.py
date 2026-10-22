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
		'{"id_": 2, "level_curve": [20, 20, 20, 20, 20, 20, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10], "xp_curve": [400, 700, 1600, 2800, 4300, 6100, 8200, 10600, 13300, 16300], "rarity": "Normal", "max_levels": [1, 20, 90], "unlock_method": "Stage", "forms": [{"name": "Tank Cat", "description": ["Acts as a shield with the great health.", "Their Area attacks are strong enough to move a pebble."], "health": 400, "knockbacks": 1, "speed": 16, "damage": 2, "standing_range": 110, "area_targeting": true, "wave": null, "surge": null, "death_surge": null, "blast": null, "slow": null, "freeze": null, "knockback": null, "weaken": null, "warp": null, "curse": null, "toxic": null, "dodge": null, "target_only": null, "counter_surge": null, "wave_block": null, "barrier": null, "survive": null, "shield": null, "revive": null, "strengthen": null, "behemoth_dodge": null, "metal": null, "suicide": null, "zombie_killer": null, "soul_strike": null, "double_bounty": null, "base_destroyer": null, "barrier_break": null, "shield_break": null, "critical": null, "savage_blow": null, "burrow": null, "conjure": null, "metal_killer": null, "immunities": [], "resistances": [], "traits": "", "pseudotraits": "", "breakup": {"hits": [{"damage": 2, "foreswing": 8}], "backswing": 8, "cooldown": 60}, "id_": [2, 0], "cooldown": 120, "cost": 150}, {"name": "Wall Cat", "description": ["Rigid defense, now with corners.", "Their Area attacks are strong enough to move a small rock."], "health": 400, "knockbacks": 1, "speed": 16, "damage": 2, "standing_range": 110, "area_targeting": true, "wave": null, "surge": null, "death_surge": null, "blast": null, "slow": null, "freeze": null, "knockback": null, "weaken": null, "warp": null, "curse": null, "toxic": null, "dodge": null, "target_only": null, "counter_surge": null, "wave_block": null, "barrier": null, "survive": null, "shield": null, "revive": null, "strengthen": null, "behemoth_dodge": null, "metal": null, "suicide": null, "zombie_killer": null, "soul_strike": null, "double_bounty": null, "base_destroyer": null, "barrier_break": null, "shield_break": null, "critical": null, "savage_blow": null, "burrow": null, "conjure": null, "metal_killer": null, "immunities": [], "resistances": [], "traits": "", "pseudotraits": "", "breakup": {"hits": [{"damage": 2, "foreswing": 8}], "backswing": 8, "cooldown": 60}, "id_": [2, 1], "cooldown": 120, "cost": 150}, {"name": "Eraser Cat", "description": ["Can take a beating thanks to elasticity.", "Really Good\\u2122 Defense.", "Their Area attacks are strong enough to move two small rocks."], "health": 600, "knockbacks": 1, "speed": 16, "damage": 4, "standing_range": 110, "area_targeting": true, "wave": null, "surge": null, "death_surge": null, "blast": null, "slow": null, "freeze": null, "knockback": null, "weaken": null, "warp": null, "curse": null, "toxic": null, "dodge": null, "target_only": null, "counter_surge": null, "wave_block": null, "barrier": null, "survive": null, "shield": null, "revive": null, "strengthen": null, "behemoth_dodge": null, "metal": null, "suicide": null, "zombie_killer": null, "soul_strike": null, "double_bounty": null, "base_destroyer": null, "barrier_break": null, "shield_break": null, "critical": null, "savage_blow": null, "burrow": null, "conjure": null, "metal_killer": null, "immunities": [], "resistances": [], "traits": "", "pseudotraits": "", "aliases": ["eraser"], "breakup": {"hits": [{"damage": 4, "foreswing": 8}], "backswing": 8, "cooldown": 60}, "id_": [2, 2], "cooldown": 120, "cost": 150}]}',
		['[**Rarity:** Normal]  [**Unlock Method:** Stage]', '[**Max Level**: 1(->20) + 90]']
	),
]

TEST_FORMS = [
	(
		'Eraser Cat',
		'{"name": "Eraser Cat", "description": ["Can take a beating thanks to elasticity.", "Really Good\\u2122 Defense.", "Their Area attacks are strong enough to move two small rocks."], "health": 600, "knockbacks": 1, "speed": 16, "damage": 4, "standing_range": 110, "area_targeting": true, "immunities": [], "resistances": [], "traits": "", "pseudotraits": "", "aliases": ["eraser"], "breakup": {"hits": [{"damage": 4, "foreswing": 8}], "backswing": 8, "cooldown": 60}, "id_": [2, 2], "cooldown": 120, "cost": 150}',
		['[**Cost:** 150]  [**Cooldown:** 60f]', '[**HP:** 16,200]  [**KB Count:** 1]  [**Atk:** 107]  [**DPS:** 47.91]', '[**Timings**: ↑8f / ↓8f / ⏲51f]', '[**Range:** 110]  [**Area?:** True]  [**Speed:** 8]']
	),
	(
		'Awakened Naala',
		'{"name": "Awakened Naala", "description": ["Holy beast who finds beauty amidst chaotic desire.", "Colossus/Behemoth Slayer. Strong vs Relics, ", "100% chance to Weaken (Area Atk)"], "health": 5000, "knockbacks": 2, "speed": 32, "damage": 1680, "standing_range": 300, "area_targeting": true, "weaken": {"chance": 100, "duration": 120, "to": 50}, "behemoth_dodge": {"chance": 5, "duration": 30}, "immunities": ["Curse", "Surge", "Wave"], "resistances": [], "traits": "Relic", "pseudotraits": "Behemoth | Colossus", "aliases": ["anaala"], "breakup": {"hits": [{"use_ability": true, "separate_range": [1, 300], "damage": 1680, "foreswing": 40}, {"use_ability": true, "separate_range": [300, 200], "damage": 1680, "foreswing": 60}, {"use_ability": true, "separate_range": [500, 200], "damage": 1680, "foreswing": 80}], "backswing": 56, "cooldown": 92}, "id_": [654, 2], "mults": ["Strong"], "cooldown": 1950, "cost": 4500}',
		['[**Cost:** 4,500]  [**Cooldown:** 121.20s]', '[**HP:** 135,000]  [**KB Count:** 2]  [**Atk:** 136,080]  [**DPS:** 23,873.68]', '**Timings:**\n ↑40f: **__45360__** [1~301]\n ↑20f: **__45360__** [300~500]\n ↑20f: **__45360__** [500~700]\n ↓56f / ⏲35f\n', '[**Range:** 300]  [**Area?:** True]  [**Speed:** 16]', '**Abilities:**\n— 100% chance to weaken to 50% for 120f\n', '**Passives:**\n— immune to curse, surge, wave \n— 5% chance to dodge behemoth attacks for 30f\n', '**Targets:**\n<:mult_strong:0> vs. <:trait_relic:0> | <:ptrait_behemoth:0><:ptrait_colossus:0>']
	),
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
