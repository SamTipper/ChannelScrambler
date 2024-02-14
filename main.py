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

  msg = await ctx.send(embed=embed) if msg == None else await msg.edit(embed=embed)
  return msg


@client.slash_command()
@commands.cooldown(1, 300, commands.BucketType.guild)
async def shuffle(ctx):
  await ctx.respond()
  vcs = ctx.guild.voice_channels
  immutable_length = len(vcs) # Keeping this stored instead of using ctx.guild.voice_channels just incase the length changes during execution
  msg = await embed(ctx, "Shuffling", 0, None, immutable_length)

  for index in range(immutable_length): # Main loop

    channel = choice(vcs)
    await channel.edit(position=randint(0, immutable_length), sync_permissions=True)

    vcs.pop(vcs.index(channel))
    await embed(ctx, "Shuffling", round(((index+1) / immutable_length)* 100, 2), msg, immutable_length)

  await embed(ctx, "Finished Shuffling", 100, msg, immutable_length)


client.run(TOKEN)
