# Kijiji Bot
# Uses Python 3.7

# Discord specific imports
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
# Miscellaneous imports
import os
from pathlib import Path
import json	

# Scripts running location. Only set if called via python.exe
__location__ = os.path.realpath(
	# From https://docs.python.org/3/library/os.path.html
	# If a component is an absolute path, all previous components are thrown away and joining continues from the absolute path component.
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load Configuration File
config_file_name = "bot_cfg.json"
config_file_path = Path(os.path.join(__location__,config_file_name))
if(config_file_path.is_file()):
	print("Configuration found in: {}".format(config_file_path))
	# Load the files key value pairs
	with open(config_file_path) as json_file:
	  	config_options = json.load(json_file)

	print(config_options)
else:
	print("The configuration file {} does not exist".format(config_file_path))


# Initialize the bot
default_command_prefix = "#"
if "command_prefix" in (config_options.keys()):
	defined_command_prefix = config_options["command_prefix"]
	print("Using {} as a command declaration string".format(config_options["command_prefix"]))
else:
	print("Does not appear to be a key called 'command_prefix'. Using default: {}".format(default_command_prefix ))
	defined_command_prefix = default_command_prefix

bot = commands.Bot(command_prefix=defined_command_prefix)

@bot.event
async def on_ready():
	print ("Ready when you are")
	print ("I am runing on " + bot.user.name)
	print ("With the id " + bot.user.id)
	await bot.change_presence(game=discord.Game(name='hard to get'))

@bot.command(pass_context=True)
async def ping(context,args):
	"""Verifcation that the bot is running and working."""
	await bot.say(":eight_spoked_asterisk: {}".format(args))
	await bot.say(context.message.author)
	print ("user has pinged")

@bot.command(pass_context=True)
async def test_embed(context,*args):
    embed = discord.Embed(title="Help!", description="Basically, this is how I'm used.", color=0x00a0ea)
    embed.add_field(name="{}embed".format(config_options["command_prefix"]), value="Creates a quick embed with the users input after the command is called.")
    embed.add_field(name="{}rembed".format(config_options["command_prefix"]), value="Let's you embed with more user input. After entering your message the bot will ask questions about the color and thumbnail.")
    embed.set_footer(text="Embed-This!")
    await bot.say(embed=embed)

# Run the bot using config token
if "token" in (config_options.keys()):
	# Run the bot with the supplied token
	bot.run(config_options["token"])
else:
	print("Does not appear to be a key called 'token'")