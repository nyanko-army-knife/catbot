import asyncio
import json
import random

import discord
import typing
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot as ProtoBot, BadArgument

from modules import enemies, catcombos, stages, cats
import data_catbot
from modules import aliases

intents = discord.Intents.all()

client = discord.Client(intents=intents)

class Bot(ProtoBot):
	async def on_message(self, message: Message, /) -> None:
		temp = message.content
		if not temp.startswith("!"):
			return
		if not temp.startswith("!help"):
			prefix, space, msg = temp.partition(" ")
			message.content = prefix + space + " ".join(['《' + X.strip() + '》' for X in msg.split(";") if X.strip() != ''])
		await self.process_commands(message)

bot = Bot(command_prefix='!', intents=intents, case_insensitive=True)

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, BadArgument):
		await ctx.send(error)
	else:
		raise error

with open('config/catbot_commands.json', encoding='utf-8') as f:
	commandsdata = json.load(f)

def command_metadata(com):
	inp = commandsdata[com]
	com_data = {'usage': '; '.join(inp.get('params', ''))}
	
	if inp.get('params_opt'):
		com_data['usage'] += '; __' + '; '.join(inp['params_opt']) + '__'
	
	com_data['checks'] = [lambda ctx: privilegelevel(ctx.author) < inp['tier'] and not isADM(ctx)]
	com_data['help'] = inp.get('help', inp['brief'])
	com_data['brief'] = inp['brief']
	com_data['name'] = inp['name']
	
	if inp.get('aliases'):
		com_data['aliases'] = inp.get('aliases')
	
	if ex := inp.get("examples"):
		com_data['description'] = '\n'.join([x.split(' ', 1)[0] + ' _' + x.split(' ', 1)[1] + '_' for x in ex])
	return com_data

class Help(commands.HelpCommand):
	def get_command_signature(self, command):
		if command.signature:
			return '%s%s _%s_' % (self.context.prefix, command.qualified_name, command.signature)
		else:
			return '%s%s' % (self.context.prefix, command.qualified_name)
	
	async def send_bot_help(self, mapping):
		embed = discord.Embed(title="Description")
		for cog, cmds in mapping.items():
			filtered = await self.filter_commands(cmds)
			command_signatures = [c.qualified_name for c in filtered]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "No Category")
				embed.add_field(name=cog_name, value="```" + ", ".join(command_signatures) + "```", inline=False)
		
		channel = self.get_destination()
		await channel.send(embed=embed)
	
	async def send_command_help(self, command):
		embed = discord.Embed(title='!' + command.name)
		embed.add_field(name="Syntax", value=command.usage, inline=False)
		embed.add_field(name="Help", value=command.help, inline=False)
		if command.description:
			embed.add_field(name="Examples", value=command.description, inline=False)
		if command.aliases:
			embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
		
		channel = self.get_destination()
		await channel.send(embed=embed)
	
	async def send_cog_help(self, cog):
		embed = discord.Embed(title=cog.qualified_name, description=cog.description)
		filtered = await self.filter_commands(cog.get_commands())
		command_signatures = [self.get_command_signature(c) + "\n" + c.brief for c in filtered]
		embed.add_field(name="commands", value="\n".join(command_signatures), inline=False)
		
		channel = self.get_destination()
		await channel.send(embed=embed)
	
	async def send_error_message(self, error):
		embed = discord.Embed(title="Error", description='No such command found')
		channel = self.get_destination()
		await channel.send(embed=embed)

class Miscellaneous(commands.Cog):
	@commands.command(**command_metadata('sayhi'))
	async def sayhi(self, ctx):
		answers = [['You can do better than this.'], ['Well, at least you are here.', 'You are a cat. How about that.',
																									'Look, a user said hi to me!', "A battle catter in 2021, hi to you.",
																									"You don't have anything better to do, is that so?"],
							 ["Wow, you are important, that's cool!",
								"OMG! Senpai noticed me!", "I'm happy that you are here!",
								"It's epic to have a user so cool as you in 2022!", "I wish everyone was as cool as you."],
							 ["It's a power user, it's overwhelming!", "Almost a mod for all I care.",
								"I'm gonna listen to names changed from this user.", "My friend :).",
								"The power of friendship is strong!"],
							 ["Hi moderator, how you doin'?", "Pay attention everyone, cops are here!",
								"You gotta pay respect to mods!", "Mods are moderating in 2022 too!", "Please don't ban me!"],
							 ['Hi dad!', 'Salutations, father!', 'Greetings, creator!']]
		await ctx.send(random.choice(answers[privilegelevel(ctx.author)]))
	
	@commands.command(**command_metadata('mytier'))
	async def mytier(self, ctx):
		await ctx.send(f'Your tier is {privilegelevel(ctx.author)}')
	
	@commands.command(**command_metadata('say'))
	async def say(self, channel: discord.TextChannel, msg: str):
		await channel.send(msg)

class UnitData(commands.Cog, name="unit data"):
	"""
	Commands for fetching data related to cats
	"""
	
	@staticmethod
	def catLevelConv(level: str):
		if not level.isnumeric():
			raise BadArgument("Level must be a number")
		lvl = int(level)
		if lvl > 130 or lvl < 0:
			raise BadArgument("Level must be between 0 and 130")
		return lvl
	
	@staticmethod
	def talentLevelConv(level: str):
		if not level.isnumeric():
			return 0
		lvl = int(level)
		if lvl > 10 or lvl < 0:
			return 0
		return lvl
	
	@staticmethod
	def magConv(_mag: str):
		_mag = _mag.rstrip('%')
		if not _mag.isnumeric():
			return 100
		mag = int(_mag)
		if mag > 1000000 or mag < 1:
			return 100
		return mag
		
	@commands.command(**command_metadata('catstats'))
	async def cs(self, ctx, catstats: cats.getUnitCode, level: typing.Optional[catLevelConv] = 30):
		cat = catculator.getrow(catstats[0])
		if cat is None:
			raise BadArgument(f'Invalid code for Cat unit: {cat}')
		embedsend = catculator.getstatsEmbed(cat, level, catstats[0])
		await ctx.send(embed=embedsend)
	
	@commands.command(**command_metadata('udpcat'))
	async def udpcat(self, ctx, catstats: cats.getUnitCode):
		catrow = catculator.getrow(catstats[0])
		
		code_unit = str(catstats[0] // 3)
		await ctx.send("**UDP Entry of " + catrow.tolist()[-4] +
									 '''**\n https://thanksfeanor.pythonanywhere.com/UDP/''' + code_unit.zfill(3))
	
	@commands.command(**command_metadata('cst'))
	async def catstatsandtalentsof(self, ctx, cat: cats.getUnitCode, level: typing.Optional[catLevelConv] = 30,
																 attempt: commands.Greedy[talentLevelConv] = [10, 10, 10, 10, 10]):
		attempt += [10]*(5-len(attempt))
		talents_expl = catculator.get_talent_and_explanation(cat[0] - 2) # offset by 2 required
		talent_rows = [x[1] for x in talents_expl.iterrows()]
		
		cat_row = catculator.getrow(cat[0])
		cat_unit = cat_row.tolist()
		ep = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		
		levels_applied = []
		
		for lv, line in zip(attempt, talent_rows):
			cat_unit, ep, lv_app = catculator.apply_talent(cat_unit, line, lv, ep)
			levels_applied.append(lv_app)
		
		emb = catculator.getstatsEmbed(cat_unit, level, int(cat[0]), ep)
		
		str_expl=''
		for i, line in enumerate(talent_rows):
			str_expl += f"{line['description_text']} ({levels_applied[i]}), "
		emb.add_field(name="Talents applied", value=str(str_expl[:-2]), inline=False)
		await ctx.send(embed=emb)
	
	@commands.command(**command_metadata('talentsof'))
	async def talentsof(self, ctx, cat: cats.getUnitCode):
		# If you get here then a cat was found
		talents_expl = catculator.get_talent_and_explanation(cat[0] - 2)  # offset by 2 required
		msgout = catculator.getnamebycode(cat[0]) + " has the following talents:\n"
		for lno, line in talents_expl.iterrows():
			np = catculator.getcostoftalent(line["cost_curve"], line["max_level"])
			msgout += f"**{line['description_text']}**: " + catculator.showtalentof(line) + f" ({np} NP)\n"
		await ctx.send(msgout)
	
	@commands.command(**command_metadata('enemystats'))
	async def es(self, ctx, enemystats: enemies.getUnitCode,
							 mag_hp: typing.Optional[magConv] = 100, mag_atk: typing.Optional[magConv] = -1):
		try:
			len(enemystats[0])
		except TypeError:
			enemystats[0] = [enemystats[0]]
		enemy = enemyculator.getrow(enemystats[0][0])
		if enemy is None:
			raise BadArgument('Invalid code for enemy unit.')
		magnification = mag_hp
		mag2 = mag_atk
		if mag_atk < 0:
			mag2 = mag_hp
		embedsend = enemyculator.getstatsembed(enemy, magnification, mag2)
		await ctx.send(embed=embedsend)
	
	@commands.command(**command_metadata('comboname'))
	async def comboname(self, ctx, combo_name: str):
		await ctx.send(catcombos.name_to_combo(combo_name))
	
	@commands.command(**command_metadata('combowith'))
	async def combowith(self, ctx, cat: cats.getUnitCode):
		await ctx.send(catcombos.search_by_unit(cat))
		
class StageData(commands.Cog, name="stage data"):
	@commands.command(**command_metadata('whereis'))
	async def whereis(self, ctx, *targets):
		await ctx.send(stagedata.whereistheenemy([enemies.getUnitCode(x) for x in targets]))
	
	"""
	@commands.command(**paramhandler('whereismonthly'))
	async def whereismonthly(self, ctx, targets: Greedy[enemies.getUnitCode]):
		await ctx.send(stagedata.whereisthenemymonthly(*targets))
	
	@commands.command(**paramhandler('whereisb'))
	async def whereisbeta(self, ctx, *, msg):
		pass
	"""
	
	@staticmethod
	def story_decode(msg):
		F1, F2 = False, False
		cc, ch = '', ''
		i = 0
		for i in range(1, 4):
			if str(i) in msg:
				cc = str(i)
				F1 = True
				break
		p = msg.replace(str(i), '')
		
		for i in ['itf', 'cotc', 'eoc']:
			if i in p:
				ch = i
				p = p.replace(i, '').strip()
				F2 = True
				if 'zombie' in p:
					cc += ' zombie'
					p = p.replace('zombie', '').strip()
				break
		
		return (F1 and F2, [p, ch + " ch." + cc, "ch"])
	
	@commands.command(**command_metadata('stage'))
	async def stage(self, ctx, stage: str, stg_map: typing.Optional[str] = '',
									category: typing.Optional[str] = ''):
		stageid = stagedata.getstageid(stage, 5, stg_map, category)
		# await ctx.send(stageid)
		# return
		if isinstance(stageid, list):
			return await ctx.send("You need to be more specific")
		if stageid < 0:  # something failed
			if stageid == -1:  # too many errors
				await ctx.send("That stage doesn't exist.")
			elif stageid == -2:  # could not tell between more than 1 stage
				await ctx.send("You need to be more specific.")
			elif stageid == -3:  # empty intersection
				await ctx.send("The combination of the stage, map and category produces no result.")
			elif stageid is None:
				await ctx.send("Catbot is confused and doesn't know what happened.")
			return
		stageinfo = stagedata.idtostage(stageid)
		stageenemies = stagedata.idtoenemies(stageid)
		stagetimed = stagedata.idtotimed(stageid)
		stagereward = stagedata.idtoreward(stageid)
		stagerestrictions = stagedata.idtorestrictions(stageid)
		embedtosend = stagedata.makeembed(stageinfo, stageenemies, stagetimed, stagereward, stagerestrictions, stageid)
		if len(stageenemies) > 25:  # embed won't show everything
			sending = "First 25 enemies / " + str(embedtosend.footer.text)
			embedtosend.set_footer(text=sending)
		else:
			sending = "All enemies / " + str(embedtosend.footer.text)
			embedtosend.set_footer(text=sending)
		await ctx.send(embed=embedtosend)

class Aliases(commands.Cog):
	# FUTURE - FIX THIS WITH SUBCOMMANDS
	@commands.command(**command_metadata('renamecat'))
	async def renamecat(self, ctx, cat: cats.getUnitCode, alias: str):
		aliases.register_alias("cats", cat[0], alias)
		await ctx.send('The name ' + alias + ' is now assigned.')
	
	@commands.command(**command_metadata('renameenemy'))
	async def renameenemy(self, ctx, enemy: enemies.getUnitCode, alias: str):
		aliases.register_alias("enemies", enemy[0], alias)
		await ctx.send('The name ' + alias + ' is now assigned.')
		
	@commands.command(**command_metadata('renamestage'))
	async def renamestage(self, ctx, stage: stages.getstageid, alias: str):
		aliases.register_alias("stages", stage, alias)
		await ctx.send('The name ' + alias + ' is now assigned.')
	
	@commands.command(**command_metadata('catnamesof'))
	async def catnamesof(self, ctx, cat: str):
		catstats = cats.getUnitCode(cat)
		names = aliases.aliases_of("cats", catstats[0])
		if len(names) > 0:
			await ctx.send(f"The aliases of {cat} are: {', '.join(names)}")
		else:
			await ctx.send(f"{cat} has no aliases")
	
	@commands.command(**command_metadata('enemynamesof'))
	async def enemynamesof(self, ctx, enemy: str):
		enemystats = enemies.getUnitCode(enemy)
		names = aliases.aliases_of("enemies", enemystats[0])
		if len(names) > 0:
			await ctx.send(f"The aliases of {enemy} are: {', '.join(names)}")
		else:
			await ctx.send(f"{enemy} has no aliases")
	
	@commands.command(**command_metadata('stagenamesof'))
	async def enemynamesof(self, ctx, stage: str):
		stagestats = stages.getstageid(stage)
		names = aliases.aliases_of("stages", stagestats)
		if len(names) > 0:
			await ctx.send(f"The aliases of {stage} are: {', '.join(names)}")
		else:
			await ctx.send(f"{stage} has no aliases")
	
	@commands.command(**command_metadata('deletecatname'))
	async def deletecatname(self, ctx, cat_name: str):
		aliases.deregister_alias("cats", cat_name)
		await ctx.send("Name deleted successfully.")
	
	@commands.command(**command_metadata('deleteenemyname'))
	async def deleteenemyname(self, ctx, enemy_name: str):
		aliases.deregister_alias("enemies", enemy_name)
		await ctx.send("Name deleted successfully.")
		
	@commands.command(**command_metadata('deletestagename'))
	async def deleteenemyname(self, ctx, enemy_name: str):
		aliases.deregister_alias("stages", enemy_name)
		await ctx.send("Name deleted successfully.")

def privilegelevel(member):
	return catbotdata.roledata.get(member, 1)

def isADM(ctx):
	if isinstance(ctx.channel, discord.DMChannel):
		return True
	return False

"""
def isInServer(member):
	legit_members = bot.get_guild(catbotdata.requireddata['server-id']).members  # server id
	if member in legit_members:
		return True
	return False

def serveruser(member):
	legit_members = bot.get_guild(catbotdata.requireddata['server-id'])  # server id
	if member in legit_members.members:
		return legit_members.get_member(member.id)
	return False
"""

asyncio.run(bot.add_cog(UnitData(bot)))
asyncio.run(bot.add_cog(StageData(bot)))
asyncio.run(bot.add_cog(Aliases(bot)))
asyncio.run(bot.add_cog(Miscellaneous(bot)))

bot.help_command = Help()
enemyculator = enemies
catculator = cats
catbotdata = data_catbot
stagedata = stages
bot.run(catbotdata.requireddata['auth-token'])
