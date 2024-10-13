import sqlite3

import pandas as pd
from discord import Embed as emb
import math
from collections import defaultdict
from modules import aliases

from discord.ext.commands import BadArgument

_cats = pd.read_csv('databases/auto_units.tsv', sep='\t')

try:
	_levelcurves = pd.read_csv('databases/unitlevel.csv', header=None)
except FileNotFoundError:
	raise ImportError("Level Curves file not found")
try:
	with sqlite3.connect('databases/talents.db') as conn:
		_talents_df = pd.read_sql('SELECT * FROM talents', conn)
		_tlnt_curves_df = pd.read_sql('SELECT * FROM curves', conn, index_col="lvID") \
			.fillna(0)\
			.astype('int32', errors='ignore')
		_tlnt_desc_df = pd.read_sql('SELECT * FROM talents_explanation', conn, index_col='description_id')
except sqlite3.OperationalError:
	raise ImportError("Talents Database not found")

def getcostoftalent(curve, level):
	level = max(level, 1)  # PONOS is stupid and makes max level 0 sometimes
	results = _tlnt_curves_df.loc[curve]
	return sum(results.iloc[1:1 + level])

def showtalentof(talent):
	talent_to_apply = talent["description"]
	
	min_param1, min_param2, min_param3, min_param4 = \
		talent[["min_first_parameter", "min_second_parameter", "min_third_parameter", "min_fourth_parameter"]]
	max_param1, max_param2, max_param3, max_param4 = \
		talent[["max_first_parameter", "max_second_parameter", "max_third_parameter", "max_fourth_parameter"]]
	
	message = 'Placeholder'
	if talent_to_apply == 1:  # weaken
		message = f"Gains a {min_param1}% chance to weaken targeted enemies to {100 - min_param3}%, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 2:  # freeze
		message = f"Gains a {min_param1}% chance to freeze targeted enemies, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 3:  # slow
		message = f"Gains a {min_param1}% chance to slow targeted enemies, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 4:  # target only
		message = "Gains the Target Only ability against its target traits"
	elif talent_to_apply == 5:  # strong
		message = "Gains the Strong ability against its target traits"
	elif talent_to_apply == 6:  # resist
		message = "Gains the Resistant ability against its target traits"
	elif talent_to_apply == 7:  # massive damage
		message = "Gains the Massive ability against its target traits"
	elif talent_to_apply == 8:  # knockback
		message = f"Gains a chance to knock back targeted enemies, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 9:  # warp (unused)
		pass
	elif talent_to_apply == 10:  # strengthen
		message = f"Gains an attack boost at {100 - min_param1}% HP, increasing from {min_param2}% to {max_param2}%"
	elif talent_to_apply == 11:  # survive
		message = f"Gains a chance to survive a Lethal Strike, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 12:  # base destroyer
		message = "Gains the Base Destroyer ability"
	elif talent_to_apply == 13:  # critical (unused)
		pass
	elif talent_to_apply == 14:  # zombie killer
		message = "Gains the Zombie Killer ability"
	elif talent_to_apply == 15:  # barrier breaker
		message = f"Gains a chance to Break Barriers, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 16:  # double cash
		message = "Gains the Double Bounty ability"
	elif talent_to_apply == 17:  # wave attack
		message = f"Gains a chance to make a level {max_param2} wave, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 18:  # resists weaken
		message = f"Reduces duration of Weaken, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 19:  # resists freeze
		message = f"Reduces duration of Freeze, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 20:  # resists slow
		message = f"Reduces duration of Slow, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 21:  # resists knockback
		message = f"Reduces distance of Knockback, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 22:  # resists waves
		message = f"Reduces damage of Curse, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 23:  # wave immune (unused)
		pass
	elif talent_to_apply == 24:  # warp block (unused)
		pass
	elif talent_to_apply == 25:  # curse immunity
		message = "Gains immunity to Curse"
	elif talent_to_apply == 26:  # resist curse
		message = f"Reduces duration of Curse, increasing from {min_param1}% upto {max_param1}%"
	elif talent_to_apply == 27:  # hp up
		message = f"Increases HP by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 28:  # atk up
		message = f"Increases Damage by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 29:  # speed up
		message = f"Increases Speed by {min_param1} per level upto {max_param1}"
	elif talent_to_apply == 30:  # knockback chance up (unused)
		pass
	elif talent_to_apply == 31:  # cost down
		message = f"Reduces Cost of unit, increasing from {min_param1} to {max_param1}"
	elif talent_to_apply == 32:  # recharge down
		message = f"Reduces Cooldown of unit, increasing from {min_param1}f to {max_param1}f"
	elif talent_to_apply == 33:  # target red
		message = "Gains Red as a target trait"
	elif talent_to_apply == 34:  # target floating
		message = "Gains Floating as a target trait"
	elif talent_to_apply == 35:  # target black
		message = "Gains Black as a target trait"
	elif talent_to_apply == 36:  # target metal
		message = "Gains Metal as a target trait"
	elif talent_to_apply == 37:  # target angel
		message = "Gains Angel as a target trait"
	elif talent_to_apply == 38:  # target alien
		message = "Gains Alien as a target trait"
	elif talent_to_apply == 39:  # target zombies
		message = "Gains Zombie as a target trait"
	elif talent_to_apply == 40:  # target relic
		message = "Gains Relic as a target trait"
	elif talent_to_apply == 41:  # target traitless
		message = "Gains White as a target trait"
	elif talent_to_apply == 42:  # weaken duration up
		message = f"Increases duration of Weaken, from {min_param2} to {max_param2}"
	elif talent_to_apply == 43:  # freeze duration up
		message = f"Increases duration of Freeze, from {min_param2} to {max_param2}"
	elif talent_to_apply == 44:  # slow duration up
		message = f"Increases duration of Slow, from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 45:  # knockback chance up
		message = f"Increases distance of Knockback, from {min_param1} to {max_param1}"
	elif talent_to_apply == 46:  # strengthen power up
		message = f"Increases amount of Strengthen, from {min_param1} to {max_param1}"
	elif talent_to_apply == 47:  # survive chance
		message = f"Increases chance of Survivor by {min_param1} upto {max_param1}"
	elif talent_to_apply == 48:  # critical chance
		message = f"Increases chance of a Critical Attack by {min_param1} upto {max_param1}"
	elif talent_to_apply == 49:  # barrier breaker chance
		message = f"Increases chance of breaking enemy barrier by {min_param1} upto {max_param1}"
	elif talent_to_apply == 50:  # wave chance (unused)
		pass
	elif talent_to_apply == 51:  # warp duration (unused)
		pass
	elif talent_to_apply == 52:  # critical
		message = f"Gains a {min_param1}% chance to deal a Critical Attack"
	elif talent_to_apply == 53:  # weaken immune
		message = "Gains immunity to Weaken"
	elif talent_to_apply == 54:  # freeze immune
		message = "Gains immunity to Freeze"
	elif talent_to_apply == 55:  # slow immune
		message = "Gains immunity to Slow"
	elif talent_to_apply == 56:  # knockback immune
		message = "Gains immunity to Knockback"
	elif talent_to_apply == 57:  # wave immune
		message = "Gains immunity to Waves"
	elif talent_to_apply == 58:  # warp block
		message = "Gains immunity to Warp"
	elif talent_to_apply == 59:  # savage blow
		message = f"Gains a chance to deal a Savage Blow (does {round(1 + min_param2 / 100, 2)}x damage), increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 60:  # dodge
		message = f"Gains a {min_param1}% chance to dodge attacks, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 61:  # savage blow chance (unused)
		pass
	elif talent_to_apply == 62:  # dodge duration (unused)
		pass
	elif talent_to_apply == 63:  # slow chance
		message = f"Increases slow chance by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 64:  # resist toxic
		message = f"Reduces damage from Toxic by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 65:  # toxic immune
		message = "Gains immunity to Toxic"
	elif talent_to_apply == 66:  # resist surge
		message = f"Reduces damage from Surge by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 67:  # surge immune
		message = "Gains immunity to Surge"
	elif talent_to_apply == 68:  # surge attack
		message = f"Gains a chance to make a level {min_param2} Surge between {min_param3 / 4}~{min_param3 / 4 + min_param4 / 4} range, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 69:  # slow relic
		message = f"Gains a {min_param1}% chance to slow Relic enemies, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 70:  # weaken relic
		message = f"Gains a {min_param1}% chance to weaken Relic enemies to {100 - min_param3}%, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 71:  # weaken alien
		message = f"Gains a {min_param1}% chance to weaken Alien enemies to {100 - min_param3}%, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 72:  # slow metal
		message = f"Gains a {min_param1}% chance to slow Metal enemies, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 73:  # knockback zombies
		message = f"Gains a chance to knock back Zombie enemies, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 74:  # freeze chance up
		message = f"Increases freeze chance by {min_param1}% per level upto {max_param1}%"
	elif talent_to_apply == 75:  # knockback alien
		message = f"Gains a chance to knock back Alien enemies, increasing from {min_param1}% to {max_param1}%"
	elif talent_to_apply == 76:  # freeze metal
		message = f"Gains a {min_param1}% chance to freeze Metal enemies, with duration increasing from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 77:  # target aku
		message = "Gains Aku as a target trait"
	elif talent_to_apply == 79:  # maybe soul killer
		message = "Gains Soul Strike ability"
	elif talent_to_apply == 80:  # curse
		message = f"Grants {min_param1}% curse rate against target traits, with duration from {min_param2}f to {max_param2}f"
	elif talent_to_apply == 81:  # dodge up
		message = f"Increases Dodge chance by {min_param1}% per level upto {max_param1}%"
	return message

def getrow(row):
	if row >= 0:
		try:
			returned = _cats.iloc[row]
			return returned
		except IndexError:
			pass
	raise BadArgument("Cat doesn't have a row")

def getnamebycode(cat_id):
	returned = None
	try:
		returned = _cats.iloc[cat_id][-4]
	except IndexError:
		pass
	return returned

def getUnitCode(identifier: str, errors=6):
	if identifier.isnumeric():
		locator = [int(identifier), 0]
	else:
		locator = closeEnough(identifier, errors)
		if locator is None:
			raise BadArgument(f"Cat '{identifier}' could not be found")
		if len(locator[0]) > 1:
			raise BadArgument(f"Cat '{identifier}' is not unique")
		locator[0] = locator[0][0]
	return locator

def getstatsEmbed(cat, level, unitcode, extraparam=[]):
	isinline = True
	title = 'Stats of ' + cat[-6]
	if len(cat[-6]) > 1:
		title = 'Stats of ' + cat[-4]
	whichform = unitcode
	if whichform % 3 == 0:
		title += ' - First form'
	elif whichform % 3 == 1:
		title += ' - Evolved form'
	else:
		title += ' - True form'
	title += ' - Unitcode: ' + str(whichform) + ' (' + str(int(whichform / 3)) + '-' + str(int(whichform % 3)) + ')'
	catEmbed = emb(description=title, color=0xff3300)
	catEmbed.set_author(name='Cat Bot')
	
	rarities = ['Normal Rare', 'Special Rare', 'Rare', 'Super Rare', 'Uber Super Rare', 'Legend Rare']
	rarity = rarities[cat[-5]]
	catEmbed.add_field(name='Level - Rarity', value=str(level) + ' - ' + rarity, inline=isinline)
	
	lvmult = levelMultiplier(_levelcurves.loc[unitcode // 3], level) / 100
	lives_once = ''
	if cat[58] > 0:
		lives_once = ' (hits once then dies)'
	hpv = str(math.ceil(int(cat[0]) * lvmult * 2.5)) + ' HP' + lives_once + ' - ' + str(round(int(cat[1]), 0)) + ' KB'
	catEmbed.add_field(name='HP - Knockbacks', value=hpv, inline=isinline)
	if len(extraparam) > 0:
		talent_atk = extraparam[8]
	else:
		talent_atk = 1
	dmg = str(round(math.floor(
		math.floor(round(cat[3] * lvmult * 2.5)) * max(1, talent_atk))))
	tba = round(int(cat[-2]) / 30, 2)
	if int(cat[59]) > 0:
		dmg += '/' + str(round(math.floor(
			math.floor(round(cat[59] * lvmult) * 2.5) * max(1, talent_atk))))
	if int(cat[60]) > 0:
		dmg += '/' + str(round(math.floor(
			math.floor(round(cat[60] * lvmult) * 2.5) * max(1, talent_atk))))
	dps = ' Damage - ' + str(round(30 * math.floor(
		round(int(cat[3] + cat[59] + cat[60]) * lvmult) * 2.5 * max(1, talent_atk)) / int(cat[-2]))) + ' DPS'
	damagekind = ''
	if cat[12] == 1:
		damagekind += 'area'
	else:
		damagekind += 'single'
	if cat[44] > 0:
		if cat[45] > 0:
			damagekind += ', long range'
		elif cat[45] < 0:
			damagekind += ', omnistrike'
	if cat[99] > 0 or cat[102] > 0:  # multiarea attack
		damagekind += ', multiarea'
	damagetype = 'Damage (' + damagekind + ') - DPS'
	catEmbed.add_field(name=damagetype, value=dmg + dps, inline=isinline)
	catEmbed.add_field(name='Speed - Attack Frequency', value=str(round(int(cat[2]), 0)) + ' - ' + str(tba) + 's',
										 inline=isinline)
	catEmbed.add_field(name='Cost - Respawn', value=str(round(int(cat[6] * 1.5), 0)) + ' - ' + str(
		round(max(((cat[7] * 2 - 264) / 30), 2), 2)) + 's', inline=isinline)
	rangestr = ''
	if ',' in damagekind:  # it's long range or omni
		if cat[99] > 0 and cat[102] == 0:  # multiarea 1, gods this stuff is a mess
			second_range_begin = str(int(cat[100]))
			second_range_end = str(int(cat[100] + cat[101]))
			
			leftrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rightrange = str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rangestr += leftrange + ' to ' + rightrange + ' | ' + second_range_begin + ' to ' + second_range_end + '; stands at ' + str(
				round(int(cat[5])))
		
		elif cat[99] > 0 and cat[102] > 0:  # multiarea 2
			second_range_begin = str(int(cat[100]))
			second_range_end = str(int(cat[100] + cat[101]))
			
			third_range_begin = str(int(cat[103]))
			third_range_end = str(int(cat[103] + cat[104]))
			
			leftrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rightrange = str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rangestr += leftrange + ' to ' + rightrange + ' | ' + second_range_begin + ' to ' + second_range_end + ' | ' + third_range_begin + ' to ' + third_range_end + '; stands at ' + str(
				round(int(cat[5])))
		
		else:
			
			leftrange = str(max(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rightrange = str(min(round(int(cat[44]), 0), round(int(cat[44] + cat[45]))))
			rangestr += leftrange + ' to ' + rightrange + '; stands at ' + str(round(int(cat[5])))
	else:  # otherwise only range is needed
		rangestr += str(round(int(cat[5])))
	catEmbed.add_field(name='Range', value=rangestr, inline=isinline)
	catEmbed.set_thumbnail(url=cattotriaitpics(cat))
	offensivestr = ''
	if cat[23] > 0:  # strong
		offensivestr += 'Strong, '
	if cat[24] > 0:  # knockback
		offensivestr += 'Knockback ' + str(round(int(cat[24]))) + '%, '
	if cat[25] > 0:  # freezes
		offensivestr += 'Freeze ' + str(round(int(cat[25]))) + '% (' + str(round(int(cat[26]) / 30, 2)) + 's), '
	if cat[27] > 0:  # slow
		offensivestr += 'Slow ' + str(round(int(cat[27]))) + '% (' + str(round(int(cat[28]) / 30, 2)) + 's), '
	if cat[30] > 0:  # massive damage
		offensivestr += 'Massive Damage, '
	if cat[31] > 0:  # critical
		offensivestr += 'Critical ' + str(round(int(cat[31]))) + '%, '
	if cat[32] > 0:  # targets only
		offensivestr += 'Targets only, '
	if cat[33] > 0:  # cash
		offensivestr += 'Double money, '
	if cat[34] > 0:  # base destroyer
		offensivestr += 'Base destroyer, '
	if cat[35] > 0:  # wave attack
		if cat[94] > 0:  # alternative wave
			offensivestr += "Mini-wave"
		else:  # regular
			offensivestr += "Wave"
		offensivestr += ' attack ' + str(round(int(cat[35]))) + '% (' + str(
			333 + round(int(cat[36]) - 1) * 200) + ' range, level ' + str(cat[36]) + '), '
	if cat[37] > 0:  # weaken
		offensivestr += 'Weaken ' + str(round(int(cat[37]))) + '% (' + str(round(int(cat[39]))) + '% power, ' + str(
			round(int(cat[38]) / 30, 2)) + 's), '
	if cat[40] > 0:  # strengthen
		offensivestr += 'Strengthen +' + str(round(int(cat[41]))) + '% (at ' + str(round(int(cat[40]))) + '% hp), '
	if cat[52] > 0:  # zombie killer
		offensivestr += 'Zombie killer, '
	if cat[53] > 0:  # witch killer (collab)
		offensivestr += 'Witch killer, '
	if cat[70] > 0:  # barrier breaks
		offensivestr += 'Barrier breaks ' + str(round(int(cat[70]))) + '%, '
	if cat[71] > 0:  # warp, currently unused
		offensivestr += 'Warp ' + str(round(int(cat[71]))) + '% (' + str(round(int(cat[73]))) + '-' + str(
			round(int(cat[74]))) + ', ' + str(round(int(cat[72] / 30, 2))) + 's), '
	if cat[81] > 0:  # insane damage
		offensivestr += 'Insane damage, '
	if cat[82] > 0:  # savage blow
		offensivestr += 'Savage Blow ' + str(round(int(cat[82]))) + '% (' + str(
			round(int(cat[83]))) + '% extra power), '
	if cat[86] > 0:  # surge attack
		offensivestr += 'Surge Attack ' + str(round(int(cat[86]))) + '% (' + str(
			round(int(cat[87] / 4))) + '-' + str(round(int(cat[87] / 4) + int(cat[88] / 4))) + ', level ' + str(
			round(int(cat[89]))) + '), '
	if cat[92] > 0:  # curse attack
		offensivestr += 'Curses ' + str(round(int(cat[92]))) + '% for ' + str(round(cat[93] / 30, 2)) + 's, '
	if cat[95] > 0:  # shield breaks
		offensivestr += 'Shield Piercing ' + str(int(cat[95])) + '%, '
	if cat[98] > 0:  # corpse killer
		offensivestr += 'Soulstrike, '
	offensivestr = offensivestr[:-2]
	if len(offensivestr) > 3:
		catEmbed.add_field(name='Offensive abilities', value=offensivestr, inline=isinline)
	defensivestr = ''
	if cat[29] > 0:  # strong
		defensivestr += 'Resistant, '
	if cat[42] > 0:  # survive
		defensivestr += 'Survive ' + str(round(int(cat[42]))) + '%, '
	if cat[43] > 0:  # metal
		defensivestr += 'Metal, '
	if cat[46] > 0:  # wave immune
		defensivestr += 'Wave immune, '
	if cat[47] > 0:  # wave block
		defensivestr += 'Wave block, '
	if cat[48] > 0:  # knockback immune
		defensivestr += 'Knockback immune, '
	if cat[49] > 0:  # freeze immune
		defensivestr += 'Freeze immune, '
	if cat[50] > 0:  # slow immune
		defensivestr += 'Slow immune, '
	if cat[51] > 0:  # weaken immune
		defensivestr += 'Weaken immune, '
	if cat[75] > 0:  # warp immune
		defensivestr += 'Warp immune, '
	if cat[79] > 0:  # curse immune
		defensivestr += 'Curse immune, '
	if cat[80] > 0:  # insane resist
		defensivestr += 'Insanely resists, '
	if cat[84] > 0:  # dodge
		defensivestr += 'Dodge ' + str(round(int(cat[84]))) + '% (' + str(round(int(cat[85]) / 30, 2)) + 's), '
	if cat[90] > 0:  # toxic immune
		defensivestr += 'Toxic immune, '
	if cat[91] > 0:  # surge immune
		defensivestr += 'Surge immune, '
	if len(extraparam) > 0:
		if extraparam[0] > 0:
			defensivestr += 'Resist weaken ' + str(int(extraparam[0])) + '%, '
		if extraparam[1] > 0:
			defensivestr += 'Resist freeze ' + str(int(extraparam[1])) + '%, '
		if extraparam[2] > 0:
			defensivestr += 'Resist slow ' + str(int(extraparam[2])) + '%, '
		if extraparam[3] > 0:
			defensivestr += 'Resist knockback ' + str(int(extraparam[3])) + '%, '
		if extraparam[4] > 0:
			defensivestr += 'Resist waves ' + str(int(extraparam[4])) + '%, '
		if extraparam[5] > 0:
			defensivestr += 'Resist curse ' + str(int(extraparam[5])) + '%, '
		if extraparam[6] > 0:
			defensivestr += 'Resist toxic ' + str(int(extraparam[6])) + '%, '
		if extraparam[7] > 0:
			defensivestr += 'Resist surge ' + str(int(extraparam[7])) + '%, '
	defensivestr = defensivestr[:-2]
	if len(defensivestr) > 3:
		catEmbed.add_field(name='Defensive abilities', value=defensivestr, inline=isinline)
	misc_abilities = ''
	if cat[97] > 0:  # colossus killer
		misc_abilities += 'Colossus Killer, '
	if cat[77] > 0:  # eva killer
		misc_abilities += 'Eva Killer, '
	if cat[54] > 0:  # witch killer
		misc_abilities += 'Witch Killer, '
	if cat[105] > 0:  # target Behemoth
		misc_abilities += 'Behemoth Slayer, '
	if cat[106] > 0:  # Behemoth dodge
		misc_abilities += 'Behemoth dodge ' + str(round(int(cat[106]))) + '% (' + str(
			round(int(cat[107]) / 30, 2)) + 's), '
	
	misc_abilities = misc_abilities[:-2]
	atkroutine = str(round(int(cat[13])))
	if cat[63] > 0:  # first attack applies effects
		atkroutine = '__**' + atkroutine + '**__'
	if int(cat[61]) > 0:  # has a second attack
		if cat[64] > 0:  # second attack applies effect
			atkroutine += 'f / __**' + str(round(int(cat[61]))) + '**__'
		else:
			atkroutine += 'f / ' + str(round(int(cat[61])))
	if int(cat[62]) > 0:
		if cat[65] > 0:  # third attack has effect
			atkroutine += 'f / __**' + str(round(int(cat[62]))) + '**__'
		else:
			atkroutine += 'f / ' + str(round(int(cat[62])))
	atkroutine += 'f / ' + str(round(int(cat[-3]))) + 'f'  # backswing
	catEmbed.add_field(name='Attack timings', value=atkroutine, inline=isinline)
	if len(misc_abilities) > 3:
		catEmbed.add_field(name='Miscellaneous abilities', value=misc_abilities, inline=isinline)
	return catEmbed

def closeEnough(strToCmp, errors):
	strToCmp = strToCmp.lower()
	names = _cats.loc[:, 'enname'].to_list()
	names = [str(x).lower() for x in names]
	# edit distance of everything in the tsv
	dss = list(map(lambda x: edit_distance_fast(x, strToCmp, errors), names))
	
	closest = [i for i, x in enumerate(dss) if x == min(dss)]
	
	# from dictionary
	distancedict = defaultdict(list)
	_customnames = aliases.get_all_names("cats")
	for i in _customnames:
		distancedict[edit_distance_fast(strToCmp, i[1].lower(), errors)].append(i[0])
	customnames = []
	try:
		customnames = min(distancedict.items())
	except ValueError:  # empty custom names
		customnames.append(errors + 1)
	if min(dss) > errors and customnames[0] > errors:  # both were too bad
		return None
	if min(dss) < customnames[0]:  # normal names were better
		return [closest, min(dss), 'original']  # all of the closest and the distance of the closest
	elif min(dss) == customnames[0]:  # equally good names
		return [list(set(closest + customnames[1])), min(dss), 'mixed']
	else:  # custom names were better
		return [customnames[1], customnames[0], 'custom']  # the best matches of all custom names

def levelMultiplier(levelcurve, level):
	multiplier = 100
	for i in range(1, level):
		multiplier += levelcurve[i // 10]
	return multiplier

def cattotriaitpics(cat):  # for each trait, add '1' to the string if it has the trait, '0' otherwise
	trait_ids = [10, 16, 17, 18, 19, 20, 21, 22, 78, 96]
	fstr = ''.join(['1' if cat[X] > 0 else '0' for X in trait_ids])
	return 'https://raw.githubusercontent.com/ElMustacho/catbot-v1.1/master/new_pics/' + fstr + '.png'

def apply_talent(unit, talent, level, extra_param):
	MIN_LEVEL=1
	lmax = max(talent["max_level"], MIN_LEVEL)
	level = min(level, lmax)
	
	param_1, param_2, param_3, param_4 = talent[["min_first_parameter", "min_second_parameter", "min_third_parameter", "min_fourth_parameter"]]
	if lmax > MIN_LEVEL:
		scaler = (level-MIN_LEVEL)/(lmax-MIN_LEVEL)
		# linear interpolation
		param_1 += scaler * (talent["max_first_parameter"] - talent["min_first_parameter"])
		param_2 += scaler * (talent["max_second_parameter"] - talent["min_second_parameter"])
		param_3 += scaler * (talent["max_third_parameter"] - talent["min_third_parameter"])
		param_4 += scaler * (talent["max_fourth_parameter"] - talent["min_fourth_parameter"])
	talent_to_apply = talent["description"]
	
	if talent_to_apply == 1:  # weaken
		unit[37] += param_1
		unit[38] += param_2
		unit[39] += 100 - param_3
	elif talent_to_apply == 2:  # freeze
		unit[25] += param_1
		unit[26] += param_2
	elif talent_to_apply == 3:  # slow
		unit[27] += param_1
		unit[28] += param_2
	elif talent_to_apply == 4:  # target only
		unit[32] |= 1
	elif talent_to_apply == 5:  # strong
		unit[23] |= 1
	elif talent_to_apply == 6:  # resist
		unit[29] |= 1
	elif talent_to_apply == 7:  # massive damage
		unit[30] |= 1
	elif talent_to_apply == 8:  # knockback
		unit[24] += param_1
	elif talent_to_apply == 9:  # warp (unused)
		pass
	elif talent_to_apply == 10:  # strengthen
		unit[40] += 100 - param_1
		unit[41] += param_2
	elif talent_to_apply == 11:  # survive
		unit[42] += param_1
	elif talent_to_apply == 12:  # base destroyer
		unit[34] |= 1
	elif talent_to_apply == 13:  # critical (unused)
		pass
	elif talent_to_apply == 14:  # zombie killer
		unit[52] |= 1
	elif talent_to_apply == 15:  # barrier breaker
		unit[70] += param_1
	elif talent_to_apply == 16:  # double cash
		unit[33] |= 1
	elif talent_to_apply == 17:  # wave attack
		unit[35] += param_1
		unit[36] += param_2
	elif talent_to_apply == 18:  # resists weaken
		extra_param[0] = param_1
	elif talent_to_apply == 19:  # resists freeze
		extra_param[1] = param_1
	elif talent_to_apply == 20:  # resists slow
		extra_param[2] = param_1
	elif talent_to_apply == 21:  # resists knockback
		extra_param[3] = param_1
	elif talent_to_apply == 22:  # resists waves
		extra_param[4] = param_1
	elif talent_to_apply == 23:  # wave immune (unused)
		pass
	elif talent_to_apply == 24:  # warp block (unused)
		pass
	elif talent_to_apply == 25:  # curse immunity
		unit[79] |= 1
	elif talent_to_apply == 26:  # resist curse
		extra_param[5] = param_1
	elif talent_to_apply == 27:  # hp up
		unit[0] *= (1 + param_1 / 100)
	elif talent_to_apply == 28:  # atk up
		extra_param[8] = (1 + param_1 / 100)
	elif talent_to_apply == 29:  # speed up
		unit[2] += param_1
	elif talent_to_apply == 30:  # knockback chance up (unused)
		pass
	elif talent_to_apply == 31:  # cost down
		unit[6] = unit[6] - param_1
	elif talent_to_apply == 32:  # recharge down
		unit[7] = unit[7] - param_1
	elif talent_to_apply == 33:  # target red
		unit[10] |= 1
	elif talent_to_apply == 34:  # target floating
		unit[16] |= 1
	elif talent_to_apply == 35:  # target black
		unit[17] |= 1
	elif talent_to_apply == 36:  # target metal
		unit[18] |= 1
	elif talent_to_apply == 37:  # target angel
		unit[20] |= 1
	elif talent_to_apply == 38:  # target alien
		unit[21] |= 1
	elif talent_to_apply == 39:  # target zombies
		unit[22] |= 1
	elif talent_to_apply == 40:  # target relic
		unit[78] |= 1
	elif talent_to_apply == 41:  # target traitless
		unit[19] |= 1
	elif talent_to_apply == 42:  # weaken duration up
		unit[38] += param_2
	elif talent_to_apply == 43:  # freeze duration up
		unit[26] += param_2
	elif talent_to_apply == 44:  # slow duration up
		unit[28] += param_2
	elif talent_to_apply == 45:  # knockback chance up
		unit[24] += param_1
	elif talent_to_apply == 46:  # strengthen power up
		unit[41] += param_2
	elif talent_to_apply == 47:  # survive chance
		unit[42] += param_1
	elif talent_to_apply == 48:  # critical chance
		unit[31] += param_1
	elif talent_to_apply == 49:  # barrier breaker chance
		unit[70] += param_1
	elif talent_to_apply == 50:  # wave chance
		pass
	elif talent_to_apply == 51:  # warp duration (unused)
		pass
	elif talent_to_apply == 52:  # critical
		unit[31] += param_1
	elif talent_to_apply == 53:  # weaken immune
		unit[51] |= 1
	elif talent_to_apply == 54:  # freeze immune
		unit[49] |= 1
	elif talent_to_apply == 55:  # slow immune
		unit[50] |= 1
	elif talent_to_apply == 56:  # knockback immune
		unit[48] |= 1
	elif talent_to_apply == 57:  # wave immune
		unit[46] |= 1
	elif talent_to_apply == 58:  # warp block
		unit[75] |= 1
	elif talent_to_apply == 59:  # savage blow
		unit[82] += param_1
		unit[83] += param_2
	elif talent_to_apply == 60:  # dodge
		unit[84] += param_1
		unit[85] += param_2
	elif talent_to_apply == 61:  # savage blow chance
		pass
	elif talent_to_apply == 62:  # dodge duration
		pass
	elif talent_to_apply == 63:  # slow chance
		unit[27] += param_1
	elif talent_to_apply == 64:  # resist toxic
		extra_param[6] = param_1
	elif talent_to_apply == 65:  # toxic immune
		unit[90] |= 1
	elif talent_to_apply == 66:  # resist surge
		extra_param[7] = param_1
	elif talent_to_apply == 67:  # surge immune
		unit[91] |= 1
	elif talent_to_apply == 68:  # surge attack
		unit[86] += param_1
		unit[87] += param_3
		unit[88] += param_4
		unit[89] += param_2
	elif talent_to_apply == 69:  # slow relic
		unit[27] += param_1
		unit[28] += param_2
		unit[78] |= 1
	elif talent_to_apply == 70:  # weaken relic
		unit[37] += param_1
		unit[38] += param_2
		unit[39] += 100 - param_3
		unit[78] |= 1
	elif talent_to_apply == 71:  # weaken alien
		unit[37] += param_1
		unit[38] += param_2
		unit[39] += 100 - param_3
		unit[21] |= 1
	elif talent_to_apply == 72:  # slow metal
		unit[27] += param_1
		unit[28] += param_2
		unit[18] |= 1
	elif talent_to_apply == 73:  # knockback zombies
		unit[24] += param_1
		unit[22] |= 1
	elif talent_to_apply == 74:  # freeze chance up
		unit[25] += param_1
	elif talent_to_apply == 75:  # knockback alien
		unit[24] += param_1
		unit[21] |= 1
	elif talent_to_apply == 76:  # freeze metal
		unit[25] += param_1
		unit[26] += param_2
		unit[18] |= 1
	elif talent_to_apply == 77:  # target aku
		unit[96] |= 1
	elif talent_to_apply == 78:  # shield pierce
		unit[95] += param_1
	elif talent_to_apply == 79:  # maybe soul killer
		unit[98] |= 1
	elif talent_to_apply == 80:  # curse
		unit[92] += param_1
		unit[93] += param_2
	elif talent_to_apply == 81:  # dodge up
		unit[93] += param_1
	return (unit, extra_param, level)

def get_talents_by_id(unit_id):
	results = _talents_df[_talents_df['unit_id'] == unit_id // 3]
	if len(results) == 0:
		raise BadArgument("The given unit doesn't have talents.")
	return results

def get_talent_and_explanation(unit_id):
	results = _talents_df[_talents_df['unit_id'] == unit_id // 3].join(_tlnt_desc_df, on="description", how='left')
	if len(results) == 0:
		raise BadArgument(str(getnamebycode(unit_id)) + " doesn't have talents.")
	return results

def edit_distance_fast(s1, s2, errors):
	"""
	Returns the edit distance between s1 and s2,
	unless distance > errors, in which case it will
	return some number greater than errors. Uses
	Ukkonen's improvement on the Wagner-Fisher algorithm.

	Credits to clam
	"""
	cur_row = None
	# ensure that len(s1) <= len(s2)
	len1, len2 = len(s1), len(s2)
	if len(s1) > len(s2):
		s1, s2 = s2, s1
		len1, len2 = len2, len1
	# distance is at least len2 - len1
	if len2 - len1 > errors:
		return errors + 1
	prev_row = [*range(len2 + 1)]
	for i, c1 in enumerate(s1):
		cur_row = [i + 1, *([errors + 1] * len2)]
		# only need to check the interval [i-errors,i+errors]
		for j in range(max(0, i - errors), min(len2, i + errors + 1)):
			cur_row[j + 1] = min(
				prev_row[j + 1] + 1,  # skip char in s1
				cur_row[j] + 1,  # skip char in s2
				prev_row[j] + (c1 != s2[j])  # substitution
			)
		prev_row = cur_row
	return cur_row[len2]
