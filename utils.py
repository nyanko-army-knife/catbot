import json

with open("catbot/assets_cache/emojis.json") as fl:
	emojis = json.load(fl)

def emoji_by_name(name: str):
	return f'<:{name}:{emojis[name]}>'
