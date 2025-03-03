import json
import os

import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
  emojis: list[discord.Emoji] = await client.fetch_application_emojis()
  emoji_names = [emoji.name for emoji in emojis]
  for fl_name in os.listdir('data/static/icons'):
    emoji_name = fl_name.removesuffix('.png')
    if emoji_name in emoji_names:
      continue
    with open('data/static/icons/' + fl_name, 'rb') as fl:
      await client.create_application_emoji(name=emoji_name, image=fl.read())

  emojis: list[discord.Emoji] = await client.fetch_application_emojis()
  dump = {emoji.name: emoji.id for emoji in emojis}
  with open('catbot/assets_cache/emojis.json', 'w') as fl:
    json.dump(dump, fl, indent=2)
  print("dumped")


client.run(os.getenv("CATBOT_API_KEY"))
