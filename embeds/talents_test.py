import discord
from commons.models.talents import Talent, UnitTalents
from .talents import Talents

from collections import defaultdict
from itertools import zip_longest
import json
from discord.ui import TextDisplay
from catbot.embeds.units import Cat, Form
from catbot.utils import setup_icons
import catbot.utils
from commons import idx
from serde.json import from_json
import pytest

TEST_TALENTS = [
	(
		'Dark Lazer',
		(14, 2, 50),
		'{ "talents": [ { "target": "extensions.wave", "effect_min": { "Wave": { "chance": 5, "level": 6, "mini": false } }, "effect_max": { "Wave": { "chance": 15, "level": 6, "mini": false } }, "np_curve": [ 50, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Wave", "text": "5% to 15% chance to make a level 6 wave", "max_level": 10, "is_ultra": false },  { "target": "immunities", "effect_min": { "Immunity": "Weaken" }, "effect_max": { "Immunity": "Weaken" }, "np_curve": [ 75 ], "name": "Weaken Immunity", "text": "gains immunity to weaken", "max_level": 1, "is_ultra": false }, { "target": "cost", "effect_min": { "StatMod": { "amount": -30, "relative": false } }, "effect_max": { "StatMod": { "amount": -300, "relative": false } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Cost down", "text": "reduces cost by 20 > 200", "max_level": 10, "is_ultra": false }, { "target": "health", "effect_min": { "StatMod": { "amount": 8, "relative": true } }, "effect_max": { "StatMod": { "amount": 80, "relative": true } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "HP up", "text": "increases HP by 8% > 80%", "max_level": 10, "is_ultra": false }, { "target": "damage", "effect_min": { "StatMod": { "amount": 8, "relative": true } }, "effect_max": { "StatMod": { "amount": 80, "relative": true } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Atk up", "text": "increases Atk by 8% > 80%", "max_level": 10, "is_ultra": false } ] }',
		['Wave (50~165NP)', 'Weaken Immunity (75NP)', 'Cost down (10~125NP)', 'HP up (10~125NP)', 'Atk up (10~125NP)'],
		['5% to 15% chance to make a level 6 wave\n', 'gains immunity to weaken\n', 'reduces cost by 20 > 200\n', 'increases HP by 8% > 80%\n', 'increases Atk by 8% > 80%\n'],
		[
			'[**Cost:** 1,140]  [**Cooldown:** 5.87s]',
			'[**HP:** 34,020]  [**KB Count:** 1]  [**Atk:** 6,417]  [**DPS:** 16,042.50]',
			'[**Timings**: ↑6f / ↓6f / ⏲0f]',
			'[**Range:** 210]  [**Area?:** False]  [**Speed:** 5]',
			'**Abilities:**\n— 15% chance to create a level 6 wave\n',
			'**Passives:**\n— immune to weaken \n',
			'**Targets:**\n<:mult_strong:0> vs. <:trait_red:0><:trait_dark:0>',
		],
	),
	(
		'Akira',
		(195, 2, 60),
		'{ "talents": [ { "target": "actives.freeze", "effect_min": { "Freeze": { "chance": 40, "duration": 39 } }, "effect_max": { "Freeze": { "chance": 40, "duration": 120 } }, "np_curve": [ 75, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Freeze", "text": "40% chance to freeze for 39f > 120f", "max_level": 10, "is_ultra": false }, { "target": "defensives.strengthen", "effect_min": { "Strengthen": { "health": 33, "by": 23 } }, "effect_max": { "Strengthen": { "health": 33, "by": 50 } }, "np_curve": [ 75, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Strengthen", "text": "strengthen at 33% HP by 23% > 50%", "max_level": 10, "is_ultra": false }, { "target": "defensives.survive", "effect_min": { "Survive": { "chance": 28 } }, "effect_max": { "Survive": { "chance": 100 } }, "np_curve": [ 75, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Survive", "text": "28% to 100% chance to survive a lethal hit", "max_level": 10, "is_ultra": false }, { "target": "health", "effect_min": { "StatMod": { "amount": 2, "relative": true } }, "effect_max": { "StatMod": { "amount": 20, "relative": true } }, "np_curve": [ 15, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "HP up", "text": "increases HP by 2% > 20%", "max_level": 10, "is_ultra": false }, { "target": "damage", "effect_min": { "StatMod": { "amount": 2, "relative": true } }, "effect_max": { "StatMod": { "amount": 20, "relative": true } }, "np_curve": [ 15, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Atk up", "text": "increases Atk by 2% > 20%", "max_level": 10, "is_ultra": false }, { "target": "traits", "effect_min": { "Targets": "Aku" }, "effect_max": { "Targets": "Aku" }, "np_curve": [ 150 ], "name": "Target Aku", "text": "gains target trait aku", "max_level": 1, "is_ultra": true }, { "target": "extensions.surge", "effect_min": { "Surge": { "chance": 10, "level": 1, "range": [ 1720, 1400 ], "mini": false } }, "effect_max": { "Surge": { "chance": 100, "level": 1, "range": [ 1720, 1400 ], "mini": false } }, "np_curve": [ 100, 15, 15, 15, 15, 25, 25, 25, 25, 25 ], "name": "Surge", "text": "10% to 100% chance to make a level 1 surge at 430~780 range", "max_level": 10, "is_ultra": true } ] }',
		['Freeze (75~235NP)', 'Strengthen (75~235NP)', 'Survive (75~235NP)', 'HP up (15~175NP)', 'Atk up (15~175NP)', 'Target Aku [+] (150NP)', 'Surge [+] (100~285NP)'],
		['40% chance to freeze for 39f > 120f\n', 'strengthen at 33% HP by 23% > 50%\n', '28% to 100% chance to survive a lethal hit\n', 'increases HP by 2% > 20%\n', 'increases Atk by 2% > 20%\n', 'gains target trait aku\n', '10% to 100% chance to make a level 1 surge at 430~780 range\n'],
		[
			'[**Cost:** 4,860]  [**Cooldown:** 137.87s]',
			'[**HP:** 115,200]  [**KB Count:** 3]  [**Atk:** 57,600]  [**DPS:** 11,006.37]',
			'[**Timings**: ↑108f / ↓44f / ⏲5f]',
			'[**Range:** 430]  [**Area?:** True]  [**Speed:** 13]',
			'**Abilities:**\n— 100% chance to create a level 1 surge between 430~780 range\n— 40% chance to freeze for 120f\n',
			'**Passives:**\n— immune to weaken, wave \n— 100% chance to survive a lethal attack\n— strengthens by +50% at 33% HP\n',
			'**Targets:**\n<:mult_strong:0> vs. <:trait_alien:0><:trait_aku:0>',
		],
	),
	(
		'Hayabusa',
		(262, 2, 60),
		'{ "talents": [ { "target": "traits", "effect_min": { "Targets": "Aku" }, "effect_max": { "Targets": "Aku" }, "np_curve": [ 100 ], "name": "Target Aku", "text": "gains target trait aku", "max_level": 1, "is_ultra": false }, { "target": "offensives.shield_break", "effect_min": { "ShieldBreak": { "chance": 4 } }, "effect_max": { "ShieldBreak": { "chance": 40 } }, "np_curve": [ 75, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Shield Pierce", "text": "4% to 40% chance to pierce shield", "max_level": 10, "is_ultra": false }, { "target": "resistances", "effect_min": { "Resist": { "to": "Curse", "by": 16 } }, "effect_max": { "Resist": { "to": "Curse", "by": 70 } }, "np_curve": [ 15, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Resist Curse", "text": "resist curse by 16 > 70%", "max_level": 10, "is_ultra": false }, { "target": "health", "effect_min": { "StatMod": { "amount": 2, "relative": true } }, "effect_max": { "StatMod": { "amount": 20, "relative": true } }, "np_curve": [ 15, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "HP up", "text": "increases HP by 2% > 20%", "max_level": 10, "is_ultra": false }, { "target": "damage", "effect_min": { "StatMod": { "amount": 2, "relative": true } }, "effect_max": { "StatMod": { "amount": 20, "relative": true } }, "np_curve": [ 15, 15, 15, 15, 15, 20, 20, 20, 20, 20 ], "name": "Atk up", "text": "increases Atk by 2% > 20%", "max_level": 10, "is_ultra": false }, { "target": "mults", "effect_min": { "AddMult": "Strong" }, "effect_max": { "AddMult": "Strong" }, "np_curve": [ 150 ], "name": "Strong", "text": "gains strong ability", "max_level": 1, "is_ultra": true }, { "target": "breakup.cooldown", "effect_min": { "StatMod": { "amount": -8, "relative": true } }, "effect_max": { "StatMod": { "amount": -62, "relative": true } }, "np_curve": [ 20, 20, 20, 20, 20, 25, 25, 25, 25, 25 ], "name": "TBA down", "text": "TBA reduced by 8f > 62f", "max_level": 10, "is_ultra": true }, { "target": "immunities", "effect_min": { "Immunity": "Surge" }, "effect_max": { "Immunity": "Surge" }, "np_curve": [ 150 ], "name": "Surge Immunity", "text": "gains immunity to surge", "max_level": 1, "is_ultra": true } ] }',
		['Target Aku (100NP)', 'Shield Pierce (75~235NP)', 'Resist Curse (15~175NP)', 'HP up (15~175NP)', 'Atk up (15~175NP)', 'Strong [+] (150NP)', 'TBA down [+] (20~225NP)', 'Surge Immunity [+] (150NP)'],
		['gains target trait aku\n', '4% to 40% chance to pierce shield\n', 'resist curse by 16 > 70%\n', 'increases HP by 2% > 20%\n', 'increases Atk by 2% > 20%\n', 'gains strong ability\n', 'TBA reduced by 8f > 62f\n', 'gains immunity to surge\n'],
		[
			'[**Cost:** 4,275]  [**Cooldown:** 107.87s]',
			'[**HP:** 105,600]  [**KB Count:** 7]  [**Atk:** 46,080]  [**DPS:** 17,953.25]',
			'[**Timings**: ↑32f / ↓45f / ⏲0f]',
			'[**Range:** 365 [250~650]]  [**Area?:** True]  [**Speed:** 25]',
			'**Abilities:**\n— 50% chance to slow for 100f\n— 50% chance to knockback\n',
			'**Passives:**\n— immune to slow, surge \n— resists curse [70%] \n— zombie killer\n— 40% chance to break Aku shield\n',
			'**Targets:**\n<:mult_strong:0> vs. <:trait_zombie:0><:trait_aku:0>',
		],
	),
	(
		'Ninja Cat',
		(19, 2, 50),
		'{ "talents": [ { "target": "traits", "effect_min": { "Targets": "Dark" }, "effect_max": { "Targets": "Dark" }, "np_curve": [ 75 ], "name": "Target Dark", "text": "gains target trait dark", "max_level": 1, "is_ultra": false }, { "target": "actives.dodge", "effect_min": { "Dodge": { "chance": 20, "duration": 24 } }, "effect_max": { "Dodge": { "chance": 20, "duration": 60 } }, "np_curve": [ 50, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Dodge", "text": "20% chance to dodge for 24f > 60f", "max_level": 10, "is_ultra": false }, { "target": "speed", "effect_min": { "StatMod": { "amount": 2, "relative": false } }, "effect_max": { "StatMod": { "amount": 20, "relative": false } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Spd up", "text": "increases Spd by 1 > 10", "max_level": 10, "is_ultra": false }, { "target": "health", "effect_min": { "StatMod": { "amount": 8, "relative": true } }, "effect_max": { "StatMod": { "amount": 80, "relative": true } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "HP up", "text": "increases HP by 8% > 80%", "max_level": 10, "is_ultra": false }, { "target": "damage", "effect_min": { "StatMod": { "amount": 8, "relative": true } }, "effect_max": { "StatMod": { "amount": 80, "relative": true } }, "np_curve": [ 10, 10, 10, 10, 10, 15, 15, 15, 15, 15 ], "name": "Atk up", "text": "increases Atk by 8% > 80%", "max_level": 10, "is_ultra": false } ] }',
		['Target Dark (75NP)', 'Dodge (50~165NP)', 'Spd up (10~125NP)', 'HP up (10~125NP)', 'Atk up (10~125NP)'],
		['gains target trait dark\n', '20% chance to dodge for 24f > 60f\n', 'increases Spd by 1 > 10\n', 'increases HP by 8% > 80%\n', 'increases Atk by 8% > 80%\n'],
		[
			'[**Cost:** 225]  [**Cooldown:** 60f]',
			'[**HP:** 11,664]  [**KB Count:** 3]  [**Atk:** 1,359]  [**DPS:** 1,941.43]',
			'[**Timings**: ↑6f / ↓12f / ⏲3f]',
			'[**Range:** 150]  [**Area?:** False]  [**Speed:** 20]',
			'**Abilities:**\n— 20% chance to dodge for 60f\n',
			'**Targets:**\n<:mult_strong:0> vs. <:trait_red:0><:trait_dark:0>',
		],
	)
]


@pytest.fixture(autouse=True)
def init():
	catbot.utils.emojis = defaultdict(lambda: "0")
	idx.setup()


def test_talent_embed(subtests: pytest.Subtests):
	for name, _, inp, out_names, out_values, _ in TEST_TALENTS:
		with subtests.test(msg=name):
			u_talents = from_json(UnitTalents, inp)
			embed = discord.Embed()
			o = Talents.embed_in(u_talents.talents, embed)
			for field, expected_name, expected_value in zip_longest(o.fields, out_names, out_values):
				assert field.name == expected_name
				assert field.value == expected_value


def test_form_talent_embed(subtests: pytest.Subtests, init):
	for name, (cat_id, form_id, level), inp, _, _, out_fields in TEST_TALENTS:
		with subtests.test(msg=name):
			cat = idx.units[cat_id]
			form, _ = cat.form_to_level(form_id, level)
			for talent in from_json(UnitTalents, inp).talents:
				form = talent.apply_level_to(talent.max_level, form)
			embed = catbot.utils.Embed()
			Form.embed_in(form, embed)
			for field, expected in zip_longest(embed.fields, out_fields):
				assert isinstance(field, TextDisplay)
				assert field.content == expected
