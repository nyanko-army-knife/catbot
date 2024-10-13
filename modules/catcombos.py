import sqlite3
import nltk as nl
from discord.ext.commands import BadArgument
import modules.cats as cats

try:
	conn = sqlite3.connect('databases/catcombos.db', uri=True)  # open only if exists
except sqlite3.OperationalError:  # database not found
	raise NotImplementedError("Database for cat combos not found.")
cursor = conn.cursor()

def name_to_combo(name):
	results = cursor.execute("SELECT DISTINCT combo_name FROM units_in_combo").fetchall()
	arr = [r[0] for r in results]
	search = [str(x).lower() for x in arr]
	dss = list(map(lambda x: nl.edit_distance(x, name.lower()), search))
	closest = [i for i, x in enumerate(dss) if x == min(dss)]
	if len(closest) > 1:
		raise BadArgument("Couldn't discriminate catcombo.")
	if min(dss) > 6:  # too many errors
		raise BadArgument("That combo doesn't exist.")
	results = cursor.execute(
		"select distinct required_id,combo_effect from names_effects join units_in_combo on "
		"names_effects.combo_name = units_in_combo.combo_name where names_effects.combo_name = ?",
		(arr[closest[0]],)).fetchall()
	toret = "The catcombo named **" + arr[closest[0]] + "** with the effect **" + results[0][
		1] + "** requires the following units; "
	for r in results:
		toret = toret + str(cats.getnamebycode(r[0])) + ", "
	return toret[:-2] + "."

def search_by_unit(unit_id: list[int]):  # needs tests
	results = cursor.execute(
		"select DISTINCT uic.combo_name, combo_effect, uic.required_id from names_effects join units_in_combo on names_effects.combo_name = units_in_combo.combo_name join units_in_combo as uic on uic.combo_name = names_effects.combo_name where units_in_combo.accepted_id = ?",
		(unit_id[0],)).fetchall()
	if len(results) == 0:
		return "**" + cats.getnamebycode(unit_id[0]) + "** isn't part of any combo."
	answer = "**" + cats.getnamebycode(unit_id[0]) + "** belongs to the following combos:"
	lastcombo = None
	for line in results:
		
		if line[0] != lastcombo:
			lastcombo = line[0]
			answer = answer + "\n**" + line[1] + " (" + line[0] + ")**: "
		answer = answer + str(cats.getnamebycode(line[2])) + ', '
	return answer.replace(', \n', '.\n')[:-2] + "."
