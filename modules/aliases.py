import sqlite3

from discord.ext.commands import BadArgument

try:
	conn = sqlite3.connect('databases/aliases.db')
	cursor = conn.cursor()
except sqlite3.OperationalError:
	raise ImportError("Aliases Database not provided")
	
_id_map = {"enemies": "enemy_id", "cats": "cat_id", "stages": "stage_id"}
_aliases = {"cats": [], "enemies": [], "stages": []}

for _tbl in _aliases:
	_aliases[_tbl] = cursor.execute(f'''select {_id_map[_tbl]}, alias from {_tbl}''').fetchall()

"""
def reload_db():
	global conn
	global cursor
	conn.close()
	conn = sqlite3.connect('databases/aliases.db', uri=True)
	cursor = conn.cursor()
"""

def deregister_alias(tbl: str, alias: str):
	if tbl not in ('enemies', 'cats', 'stages'):
		raise NotImplementedError("Invalid DB sent")
	if not cursor.execute(f'''select count({_id_map[tbl]}) from {tbl} where alias = ?''', (alias,)).fetchone()[0]:
		raise BadArgument("Can't delete row which doesn't exist")
	cursor.execute(f'''delete from {tbl} where alias=?;''', (alias,))
	conn.commit()
	_aliases[tbl] = cursor.execute(f'''select {_id_map[tbl]}, alias from {tbl}''').fetchall()

def register_alias(tbl: str, item_id: int, alias: str):
	if tbl not in ('enemies', 'cats', 'stages'):
		raise NotImplementedError("Invalid DB sent")
	cursor.execute(f'''insert into {tbl} values (?,?);''', (item_id, alias))
	conn.commit()
	_aliases[tbl] = cursor.execute(f'''select {_id_map[tbl]}, alias from {tbl}''').fetchall()
	
def aliases_of(tbl: str, item_id: int):
	return [als[1] for als in _aliases[tbl] if als[0] == item_id]

def get_all_names(tbl: str):
	if tbl not in ('enemies', 'cats', 'stages'):
		raise NotImplementedError("Invalid DB sent")
	return _aliases[tbl]

def alias_to_id(tbl: str, alias: str):
	if tbl not in ('enemies', 'cats', 'stages'):
		raise NotImplementedError("Invalid DB sent")
	return cursor.execute(f'''select {_id_map[tbl]} from {tbl} where alias=?''', (alias,)).fetchone()
