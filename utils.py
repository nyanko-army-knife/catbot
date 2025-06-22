import json

with open("catbot/assets_cache/emojis.json") as fl:
	emojis = json.load(fl)

with open("catbot/assets_cache/item_icons.json") as fl:
	item_icons = {int(K): V for K, V in json.load(fl).items()}


def emoji_by_name(name: str):
	return f'<:{name}:{emojis[name]}>'
