import os

import discord
from discord.ext import commands

import commons.idx as idx

idx.setup()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


def emoji_by_name(name: str):
  return f'<:{name}:{idx.emojis[name]}>'


@bot.command()
async def enemy(ctx, *args):
  target = " ".join(args)
  enem = idx.enemies.lookup(target)

  embed = discord.Embed(colour=discord.Colour.red(), title=f"{enem.name} [{enem.id_}]")

  trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in enem.traits]
  ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in enem.ptraits]
  embed.add_field(name="Traits", value="".join(trait_emojis + ptrait_emojis))
  embed.add_field(name="Atk", value=f'{enem.atk:,}', inline=True)
  embed.add_field(name="HP", value=f'{enem.hp:,}', inline=True)
  embed.add_field(name="Spd", value=enem.speed, inline=True)

  display_range = f'{enem.range_}'
  basehit = enem.breakup.hit_0
  if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
    if basehit.range_width > 0:
      display_range += f' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
    else:
      display_range += f' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

  embed.add_field(name="Range", value=display_range, inline=True)
  embed.add_field(name="Area?", value=enem.area_attack, inline=True)
  embed.add_field(name="KB Count", value=enem.kb, inline=True)
  embed.add_field(name="Drop", value=f'{enem.drop:,}', inline=True)

  if enem.breakup.hit_1 is not None:
    embed.add_field(name="Breakup", value=str(enem.breakup), inline=False)

  if enem.extensions:
    embed.add_field(name="Extensions", value='\n'.join(str(x) for x in enem.extensions), inline=False)
  if enem.passives.immunities:
    embed.add_field(name="Immunities", value='immune to ' ','.join(x.to for x in enem.passives.immunities), inline=False)
  if enem.passives.defensives:
    embed.add_field(name="Defensives", value='\n'.join(str(x) for x in enem.passives.defensives), inline=False)
  if enem.passives.offensives:
    embed.add_field(name="Offensives", value='\n'.join(str(x) for x in enem.passives.offensives), inline=False)
  if enem.abilities:
    embed.add_field(name="Actives", value='\n'.join(str(x) for x in enem.abilities), inline=False)

  fl_id = f'{enem.id_:03}'
  upload_file = discord.File(f'data/img/enemy/{fl_id}.png', filename=f'{fl_id}.png')
  embed.set_thumbnail(url=f"attachment://{fl_id}.png")
  await ctx.send(file=upload_file, embed=embed)


@bot.command()
async def cat(ctx, *args):
  target = " ".join(args)
  form = idx.forms.lookup(target)
  form = idx.units[form.id_[0]].to_level(30).forms()[form.id_[1]]

  embed = discord.Embed(colour=discord.Colour.green(), title=f"{form.name} [{form.id_[0]}-{form.id_[1]}]")

  trait_emojis = [emoji_by_name(f'trait_{trait}') for trait in form.traits]
  ptrait_emojis = [emoji_by_name(f'ptrait_{ptrait}') for ptrait in form.ptraits]
  ability_emois = [emoji_by_name(f'mult_{mult}') for mult in form.mults]
  if trait_emojis or ptrait_emojis:
    embed.add_field(name="Targets", value="".join(trait_emojis + ptrait_emojis) + "\n" + "".join(ability_emois),
                    inline=len(trait_emojis + ptrait_emojis) < 6)
  embed.add_field(name="Atk", value=f'{form.atk:,}\n({30 * form.atk / form.breakup.cd_effective:.2f} DPS)', inline=True)
  embed.add_field(name="HP", value=f'{form.hp:,}', inline=True)
  embed.add_field(name="Spd", value=form.speed, inline=True)

  display_range = f'{form.range_}'
  basehit = form.breakup.hit_0
  if not basehit.separate_range and basehit.range_width != 0:  # true if any hits have separate range
    if basehit.range_width > 0:
      display_range += f' [{basehit.range_start}~{basehit.range_start + basehit.range_width}]'
    else:
      display_range += f' [{basehit.range_start + basehit.range_width}~{basehit.range_start}]'

  embed.add_field(name="Range", value=display_range, inline=True)
  embed.add_field(name="Area?", value=form.area_attack, inline=True)
  embed.add_field(name="KB Count", value=form.kb, inline=True)
  embed.add_field(name="Cost", value=f'{form.cost:,}', inline=True)
  embed.add_field(name="Cooldown", value=f'{form.cooldown:,}f', inline=True)

  if form.breakup.hit_1 is not None:
    embed.add_field(name="Breakup", value=str(form.breakup), inline=False)
  else:
    embed.add_field(name="Timings",
                    value=f'{form.breakup.hit_0.foreswing}f/{form.breakup.backswing}f/{form.breakup.tba}f', inline=True)

  if form.extensions:
    embed.add_field(name="Extensions", value='\n'.join(str(x) for x in form.extensions), inline=False)
  if form.passives.immunities:
    embed.add_field(name="Immunities", value=', '.join(str(x) for x in form.passives.immunities), inline=False)
  if form.passives.defensives:
    embed.add_field(name="Defensives", value='\n'.join(str(x) for x in form.passives.defensives), inline=False)
  if form.passives.offensives:
    embed.add_field(name="Offensives", value='\n'.join(str(x) for x in form.passives.offensives), inline=False)
  if form.abilities:
    embed.add_field(name="Actives", value='\n'.join(str(x) for x in form.abilities), inline=False)

  fl_id = f"{form.id_[0]:03}_{form.id_[1]}"

  upload_file = discord.File(f'data/img/unit/{fl_id}.png', filename=f'{fl_id}.png')
  embed.set_thumbnail(url=f"attachment://{fl_id}.png")
  await ctx.send(file=upload_file, embed=embed)


@bot.command()
async def stage(ctx, *args):
  target = " ".join(args)
  stage = idx.stages.lookup(target)
  map_ = idx.categories[stage.id_[0]].maps[stage.id_[1]]

  embed = discord.Embed(colour=discord.Colour.yellow(), title=f"{stage.name} - {map_.name} [{stage.id_str}]",
                        )
  specs = f"length: {stage.length:,} | base hp: {stage.base_health:,} | enemy limit: {stage.enemy_limit}"
  embed.add_field(name="specs", value=specs, inline=False)

  misc = []
  if stage.no_continues: misc.append("no continues")
  if stage.boss_shield: misc.append("has boss shield")
  if misc: embed.add_field(name="misc", value=", ".join(misc), inline=False)

  for schematic in stage.schematics:
    header = (f"{'★' if schematic.is_boss else ''} "
              f"{idx.enemies.get(schematic.enemy_id).name} "
              f"({schematic.mag_str})")
    spawn_str = []
    if schematic.quantity != 1: spawn_str += [f"x {schematic.qty_str}"]
    if schematic.spawn_hp < 100: spawn_str += [f"{schematic.spawn_hp}%"]
    if schematic.score > 0: spawn_str += [f"@{schematic.score}"]
    if schematic.kill_count == 0 and (
          schematic.spawn_hp == 100 or (schematic.start > 1 and schematic.is_start_after_hp)):
      spawn_str += [f"{schematic.start}f"]
    if schematic.quantity == 0 or schematic.quantity > 1: spawn_str += [f"⟳ {schematic.respawn_str}"]
    if schematic.kill_count > 0: spawn_str += [f"💀 {schematic.kill_count}"]

    embed.add_field(
      name=header,
      value=' | '.join(spawn_str),
      inline=True
    )

  await ctx.send(embed=embed)


bot.run(os.getenv("CATBOT_API_KEY"))
