import functools
import math

from discord.ext.commands import BadArgument

from modules import aliases, enemies
from discord import Embed as emb
import sqlite3

_enemydata = enemies

conn = sqlite3.connect('databases/stages.db')
cursor = conn.cursor()

def dataToEmbed(enemylines, stagedata, magnification):
	stageEmbed = emb(description='Amount | First Spawn Frame *(Respawn F)* | Base Health',
									 color=0x009B77)
	stageEmbed.set_author(name='Cat Bot')
	stageEmbed.add_field(name='Stage data', value=enemylines[0][14])
	enemystring = ''
	for enemyline in enemylines:
		title = ''
		if enemyline[10] > 0:
			title = '**'
		title += _enemydata.namefromcode(enemyline[2]) + ', ' + str(round(enemyline[4] * magnification)) + '%'
		if enemyline[10] > 0:
			title += '**'
		
		if enemyline[3] < 1:
			enemystring += '∞'
		else:
			enemystring += str(enemyline[3])
		if enemyline[8] == 1:  # wait time after reaching % base hp
			enemystring += ' | **' + str(enemyline[11] * 2) + 'f**'
		else:
			enemystring += ' | ' + str(enemyline[11] * 2) + 'f'
		if enemyline[3] != 1:
			if enemyline[5] == enemyline[6]:
				enemystring += ' *(' + str(enemyline[5] * 2) + 'f)*'
			else:
				enemystring += ' *(' + str(enemyline[5] * 2) + '~' + str(enemyline[6] * 2) + 'f)*'
		enemystring += ' | ' + str(enemyline[7]) + '%'
		stageEmbed.add_field(name=title, value=enemystring, inline=True)
		enemystring = ''
	return stageEmbed

def getstageid(stagename, errors=5, stagelevel='', stagecategory=''):
	results = None
	query = '''select stages.stage, stages.level, stages.category, stages.stageid from stages;'''
	stage = cursor.execute(query).fetchall()
	custom_stages_for_reference = aliases.get_all_names("stages")
	stagenames_nodiff = [x[0].lower() for x in stage]
	stagenames_nodiff = [x[:x.find('(') if x.find('(') > 0 else len(x)] for x in stagenames_nodiff]
	dss = [edit_distance_fast(x, stagename, errors) for x in stagenames_nodiff]
	custom_stagenames_nodiff = [x[1].lower() for x in aliases.get_all_names("stages")]
	dss_custom = [edit_distance_fast(x, stagename, errors) for x in custom_stagenames_nodiff]
	# 1) an actual name is the best one
	# 2) a custom name is the best one
	# 3) both names sucks, in which case we check if
	# 3b) there's a good match as an actual name without the difficulty spelled in
	# 4) more than 2 any names could fit equally good, in which case
	# 4b) there's a good match if we also take in account the map for actual names
	# 4c) there's a good match if we also take in account the map and the category for actual names
	# actual names are given priority
	
	if min(dss) > errors and min(dss_custom) > errors:  # case 3
		stagenames = [x[1].lower() for x in stage]
		dss = list(map(lambda x: edit_distance_fast(x, stagename, errors), stagenames))
		if min(dss) > errors:  # case 3b
			return -1
	# FIXME throws exception if empty
	best_minimum = min(min(dss), min(dss_custom))
	nearestmatch = [i for i, x in enumerate(dss) if x == best_minimum]
	nearestmatch_custom = [i for i, x in enumerate(dss_custom) if x == best_minimum]
	all_best_matches = nearestmatch + nearestmatch_custom
	if len(all_best_matches) > 1:  # this means we have more than 2 best shots
		if stagelevel == '':
			closest = []
			closest_custom = []
			for near in nearestmatch:
				closest.append(stage[near])
			for near in nearestmatch_custom:
				closest_custom.append(custom_stages_for_reference[near])
			return [closest, closest_custom]
		else:
			stagelevels = [x[1].lower() for x in stage]
			leveldss = list(map(lambda x: edit_distance_fast(x, stagelevel, errors), stagelevels))
			if min(leveldss) > errors:
				results = -1
				raise Exception('Level could not match anything.')
			nearestlevelmatch = [i for i, x in enumerate(leveldss) if x == min(leveldss)]
			intersection1 = [value for value in nearestlevelmatch if value in nearestmatch]
			if len(intersection1) == 0:
				results = -3
				raise Exception('Empty intersection.')
			if len(intersection1) > 1:  # same level and stage name eg sweet xp
				if stagecategory == '':
					results = -2
					raise Exception('Could not discriminate.')
				else:
					stagecategories = [x[2].lower() for x in stage]
					categorydss = list(map(lambda x: edit_distance_fast(x, stagecategory, errors), stagecategories))
					if min(categorydss) > errors:
						results = -1
						raise Exception('Category could not match anything.')
					nearestcategorymatch = [i for i, x in enumerate(categorydss) if x == min(categorydss)]
					intersection2 = [value for value in intersection1 if value in nearestcategorymatch]
					if len(intersection2) == 0:
						results = -3
						raise Exception('Empty secondary intersection.')
					if len(intersection2) > 1:
						results = -2
						raise Exception('Could not discriminate.')
					else:
						results = stage[intersection2[0]][3]
			else:
				results = stage[intersection1[0]][3]
	else:  # we have exactly 1 best match
		if len(nearestmatch_custom) > 0:  # case 2
			results = aliases.alias_to_id("stages", custom_stagenames_nodiff[nearestmatch_custom[0]])[0]
		else:  # case 1
			results = stage[nearestmatch[0]][3]
	return results

def makeembed(stageinfo, stageenemies, stagetimed, stagereward, stagerestrictions, stageid):
	decsstring = 'Base hp = ' + str(stageinfo[0][4]) + ', stage length = ' + str(
		stageinfo[0][7]) + ', max enemies = ' + str(stageinfo[0][8]) + '\n'
	for reward in stagereward:
		decsstring += str(reward[0]) + '% of getting ' + str(reward[1]) + ' ' + reward[2] + ', '
	if len(stagereward) > 0:
		decsstring = decsstring[:-2] + '\n'
	for timed in stagetimed:
		decsstring += "Time score " + str(timed[0]) + " = " + str(timed[1]) + ' ' + str(timed[2]) + ', '
	if len(stagetimed) > 0:
		decsstring = decsstring[:-2] + '\n'
	decsstring += 'Difficulties ' + stageinfo[0][14]
	decsstring += ', Respawns ' + str(stageinfo[0][16]) + 'f - ' + str(stageinfo[0][17]) + 'f'
	stageEmbed = emb(title=stageinfo[0][3] + '; ' + stageinfo[0][2] + '; ' + stageinfo[0][1] + '; ' + str(stageid),
									 description=decsstring,
									 color=0x009B77)
	stageEmbed.set_author(name='Cat Bot')
	enemystring = ''
	for enemyline in stageenemies:
		title = ''
		if enemyline[1] in [1, 2]:
			title = '__**'
		magstring = enemyline[3]
		if magstring.count(magstring[1:magstring.find(',')]) > 1:
			magstring = magstring[1:magstring.find(',')] + '%'
		else:
			magstring = magstring + '%'
		title += _enemydata.namefromcode(enemyline[2]) + ', ' + magstring
		if enemyline[1] == 1:
			title += '**__'
		elif enemyline[1] == 2:
			title += ' (shakes screen) **__'
		if enemyline[4] < 1:
			enemystring += '∞'
		else:
			enemystring += str(enemyline[4])
		if enemyline[8] == 1:  # wait time after reaching % base hp
			enemystring += ' | **' + str(enemyline[6]) + 'f**'
		else:
			enemystring += ' | ' + str(enemyline[6]) + 'f'
		if enemyline[4] != 1:
			enemystring += ' *(' + str(enemyline[7]) + 'f)*'
		enemystring += ' | ' + str(enemyline[5])
		if enemyline[9] > 0:
			enemystring += ' | ' + str(enemyline[9]) + 'k'
		stageEmbed.add_field(name=title, value=enemystring, inline=True)
		enemystring = ''
	try:
		elaborate = stagerestrictions[0][1]
		stageEmbed.set_footer(text=elaborate)
	except:
		stageEmbed.set_footer(text='No restrictions')
	return stageEmbed

def nametoenemies(stringtosearch, errors):  # TODO refine failing to get data for whatever reason
	query = '''select * from searchunitstages'''  # TODO this is going to change later
	stagenames = cursor.execute(query).fetchall()
	stagenames = [x[0].lower() for x in stagenames]
	dss = list(map(lambda x: edit_distance_fast(x, stringtosearch, errors), stagenames))
	if min(dss) > errors:
		results = -1
		raise Exception('String could not match anything.')
	nearestmatch = [i for i, x in enumerate(dss) if x == min(dss)]
	if len(nearestmatch) > 1:
		results = -2
		raise Exception('Could not discriminate.')
	else:
		nearestmatch = [(stagenames[nearestmatch[0]])]
		cursor.execute('SELECT * from enemylines, stage where stage.stage_id=enemylines.stage_appearance and '
									 'LOWER(name)=?', nearestmatch)
		results = cursor.fetchall()
	return results

def whereistheenemy(enemycodes: list[list[int]], teleport=False):
	if len(enemycodes) == 0:
		raise BadArgument("No enemies found")
	loc_sets = []
	for enemycode in enemycodes:
		loc_sets.append(set(cursor.execute('SELECT DISTINCT stages.stage, stages.category, stages.level, '
																			 'stages.stageid from units join stages on units.stageid = stages.stageid where enemycode=?',
																			 [str(enemycode[0])]).fetchall()))
	loc_sets_intsn = functools.reduce(lambda a, b: a & b, loc_sets)
	results = sorted(loc_sets_intsn, key=lambda x: x[3])
	if len(results) == 0:
		return "No stages found."
	elif len(results) == 1 or teleport:  # teleport to best result by using sbid function
		return results[0]
	answer = "Stages found: "  # todo make this nicer, text wise, in respect to the number of units
	category = ''
	post_processed_stages = []
	last_stage = [-1, -1, -1, -1]
	first_good_stage = -1
	consecutive_stages = 0
	# collapse barons into less stages
	for stage in results:
		if last_stage[3] == int(stage[3]) - 1:  # can compress this stage
			if stage[3] // 100000 == 24 or stage[3] // 100000 == 27:  # barons and collab barons only
				if first_good_stage == -1:
					consecutive_stages += 1
				else:
					first_good_stage = stage
			else:  # we shouldn't compress anymore
				if consecutive_stages > 0:  # we might end up here in case of consecutive stages that really have nothing to do with the neighboor
					first_good_stage = -1
					post_processed_stages[-1][0] += ' __and the next ' + str(consecutive_stages) + ' stages__'
					consecutive_stages = 0
				post_processed_stages.append(list(stage))
		else:
			if consecutive_stages > 0:  # stop compressing
				first_good_stage = -1
				post_processed_stages[-1][0] += ' __and the next ' + str(consecutive_stages) + ' stages__'
				consecutive_stages = 0
			post_processed_stages.append(list(stage))
		last_stage = stage
	if consecutive_stages > 0:  # stop compressing, might happen if last stage could have been compressed
		post_processed_stages[-1][0] += ' __and the next ' + str(consecutive_stages) + ' stages__'
	for stage in post_processed_stages:
		if stage[1] != category:
			if answer.endswith(' - '):
				answer = answer[0:-3]
			answer += '\n**' + stage[1] + '**; '
		category = stage[1]
		answer += stage[0] + ' - '
		if len(answer) > 1900:
			answer += '*and other stages*   '
			break
	answer = answer[:-3]
	answer += '.'
	return answer

def whereisthenemymonthly(enemycodes: list[list[int]]):
	if len(enemycodes) == 0:
		raise BadArgument("No enemies found")
	loc_sets = []
	for enemycode in enemycodes:
		# TODO fix this
		loc_sets.append(set(cursor.execute('SELECT DISTINCT stages.stage, stages.category, stages.level, '
																			 'stages.stageid, stages.energy from units join stages on units.stageid = stages.stageid where enemycode=? and category=("Story Mode")',
																			 [str(enemycode[0])]).fetchall()))
	loc_sets_intsn = functools.reduce(lambda a, b: a & b, loc_sets)
	results = sorted(loc_sets_intsn, key=lambda x: x[-1])
	
	if len(results) == 0:
		return "No stages found."
	answer = "(Beta) Stages found (sorted by energy price): "  # future: make this nicer, text wise, in respect with the number of units
	category = ''
	for stage in results:
		if stage[1] != category:
			if answer.endswith(' - '):
				answer = answer[0:-3]
			answer += '\n**' + stage[1] + '**; '
		category = stage[1]
		answer += stage[0] + ' - '
		if len(answer) > 1950:
			answer += '*and other stages*   '
			break
	answer = answer[:-3]
	answer += '.'
	return answer

def listofstagesfromenemies(enemycode, name2="", name3="", enemycode1="", enemycode2=""):
	if name2 != '':
		if name3 != '':
			ret_tuple = (str(enemycode[0][0]), str(enemycode1[0][0]), str(enemycode2[0][0]))
			results = cursor.execute(
				'''SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=?
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=?
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
				ret_tuple).fetchall()
		else:
			ret_tuple = (str(enemycode[0][0]), str(enemycode1[0][0]))
			results = cursor.execute(
				'''SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=?
INTERSECT
SELECT DISTINCT stages.stage, stages.category, stages.level from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category''',
				ret_tuple).fetchall()
	else:
		results = cursor.execute(
			'SELECT DISTINCT stages.stage, stages.category from units join stages on units.stageid = stages.stageid where enemycode=? order by stages.category',
			[str(enemycode[0][0])]).fetchall()
	
	if len(results) == 0:
		return "No stages found."
	return results

def showstagesinembed(stages, index=0, showcost=False):  # todo implement showcost
	embedtoret = emb(description='test', color=0xf43967)
	embedtoret.set_author(name='Cat Bot')
	embedtoret.set_footer(text='Beta feature; showing page ' + str(math.ceil((index + 1) / 25)) + ' out of ' + str(
		math.ceil(len(stages) / 25)))
	for stage in stages[index:index + 24]:
		embedtoret.add_field(name=stage[1] + ' - ' + stage[2], value=stage[3], inline=True)
	return embedtoret

def idtoenemies(id_f):
	results = cursor.execute('select units.* from units JOIN stages on units.stageid=stages.stageid where '
													 'units.stageid = ?', [id_f]).fetchall()
	return results

def idtostage(id_f):
	results = cursor.execute('select * from stages where stageid = ?', [id_f]).fetchall()
	return results

def idtotimed(id_f):
	results = cursor.execute(
		"select time, 'reward-translation'.item, amount from timed JOIN stages on "
		"timed.stage_id=stages.stageid join 'reward-translation' on timed.item='reward-translation'.code "
		"where stages.stageid = ?",
		[id_f]).fetchall()
	return results

def idtoreward(id_f):
	results = cursor.execute(
		"SELECT chance, amount, 'reward-translation'.item from rewards join 'reward-translation' where code = rewards.item and stage_id=?;",
		[id_f]).fetchall()
	return results

def idtorestrictions(id_f):
	results = cursor.execute(
		'select "restrict".* from "restrict" JOIN stages on "restrict".stageid=stages.stageid where stages.stageid = ?',
		[id_f]).fetchall()
	return results

def edit_distance_fast(s1, s2, errors):
	"""
	Returns the edit distance between s1 and s2,
	unless distance > errors, in which case it will
	return some number greater than errors. Uses
	Ukkonen's improvement on the Wagner-Fisher algorithm.

	Credits to clam
	"""
	
	cur_row = []
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
