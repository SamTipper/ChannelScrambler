from os import environ
import discord
from random import randint, choice
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = environ['TOKEN']
intents = discord.Intents.default()
intents.message_content = True
client = discord.Bot(intents=intents)


@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.respond('Easy there tiger! This command is on a %.2fs cooldown.' % error.retry_after)
    raise error


@client.event
async def on_ready():
  print('You have logged in as {0.user}'.format(client))


async def embed(ctx, state, percentage, msg, channel_count):
  embed = discord.Embed(
    title = f'**{state} {channel_count} Voice Channels!**',
    description = "🔁" if state == "Shuffling" else "✅",
    colour = discord.Colour.gold() if state == "Shuffling" else discord.Colour.green()
  )
  embed.set_footer(text='Channel Shuffler',icon_url=client.user.avatar)
  embed.add_field(name='Progress:', value=f'{percentage}%', inline=False)

  msg = await ctx.respond(embed=embed) if msg == None else await msg.edit_original_response(embed=embed)
  return msg


@client.slash_command()
@commands.cooldown(1, 300, commands.BucketType.guild)
async def shuffle(ctx):
  vcs = ctx.guild.voice_channels
  immutable_length = len(vcs) # Keeping this stored instead of using ctx.guild.voice_channels just incase the length changes during execution
  msg = await embed(ctx, "Shuffling", 0, None, immutable_length)

  for index in range(immutable_length): # Main loop

    channel = choice(vcs)
    await channel.edit(position=randint(0, immutable_length), sync_permissions=True)

    vcs.pop(vcs.index(channel))
    await embed(ctx, "Shuffling", round(((index+1) / immutable_length)* 100, 2), msg, immutable_length)

  await embed(ctx, "Finished Shuffling", 100, msg, immutable_length)

@client.slash_command()
async def shuffletop(ctx, amount: int = 1):
  try:
    await ctx.defer()
    more_than_5 = False

    if amount > 5:
      amount = 5
      more_than_5 = True

    vcs = ctx.guild.voice_channels[1::]
    vc_names = []

    for _ in range(amount):
      new_top_channel = vcs.pop(vcs.index(choice(vcs)))
      vc_names.append(new_top_channel.name)
      await new_top_channel.edit(position=0, sync_permissions=True)

    vc_names = ", ".join(vc_names)

    if amount == 1:
      await ctx.respond(f"{vc_names} is now the top channel!")
    elif more_than_5:
      await ctx.respond(f"You can't shuffle more than 5 channels at once! Defaulting to 5.\n{vc_names} are now the top channels!")
    else:
      await ctx.respond(f"{vc_names} are now the top channels!")

  except Exception as e:
    await ctx.respond(f"An error occurred during shuffling: {str(e)}")

client.run(TOKEN)
