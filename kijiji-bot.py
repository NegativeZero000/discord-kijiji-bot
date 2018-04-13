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

# Scripts running location. Only set if called via python.exe
__location__ = os.path.realpath(
	# From https://docs.python.org/3/library/os.path.html
	# If a component is an absolute path, all previous components are thrown away and joining continues from the absolute path component.
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load Configuration File
config_file_name = "bot.cfg"
config_file_path = Path(os.path.join(__location__,config_file_name))
if(config_file_path.is_file()):
	print("Configuration found in: {}".format(config_file_path))
	# Load the files key value pairs
	config_options = {}	
	with open(config_file_path) as config_file:
		for line in config_file:
			if "=" in line:
				key,value = line.split("=",1)
				config_options[key.strip().lower()] = value
else:
	print("The configuration file {} does not exist".format(config_file_path))


# Initialize the bot
default_command_prefix = "#"
if "command_prefix" in (config_options.keys()):
	defined_command_prefix = config_options["token"]
else:
	print("Does not appear to be a key called 'command_prefix'. Using default: {}".format(default_command_prefix ))
	defined_command_prefix = default_command_prefix

bot = commands.Bot(command_prefix=defined_command_prefix)

@bot.event
async def on_ready():
	print ("Ready when you are")
	print ("I am runing on " + bot.user.name)
	print ("With the id " + bot.user.id)
	await client.change_presence(game=discord.Game(name='Pining in the fjords'))

@bot.command(pass_context=True)
async def ping(context):
	"""Verifcation that the bot is running and working."""
	await bot.say(":eight_spoked_asterisk: Hello!! :smile:")
	print ("user has pinged")

# Run the bot using config token
if "token" in (config_options.keys()):
	# Run the bot with the supplied token
	bot.run(config_options["token"])
else:
	print("Does not appear to be a key called 'token'")