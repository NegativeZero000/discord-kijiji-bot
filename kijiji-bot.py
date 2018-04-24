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
import datetime
import re
import random

class KijijiListing(object):
    '''The basic Kijiji Listing information'''

    def __init__(self, dictionary):
        self.url = dictionary['absoluteurl']
        self.imageurl = dictionary['imageurl']
        self.id = dictionary['id']
        self.posted = dictionary['postedasdate']
        self.title = dictionary['title']
        self.description = dictionary['shortdescription']
        self.location = dictionary['location']
        self.price = dictionary['price']

    def __str__(self):
        return 'Title: {}\nDescription: {}\nPrice: {}\nURL: {}'.format(
            self.title, self.description, self.price, self.url
        )

    def to_embed(self):
        '''Created a discord embed from this instances properties'''
        listing_embed = discord.Embed(title=self.title, description=self.description,
                                      color=discord.Colour(hex(random.randint(0, 16777215))),
                                      url=self.url)
        listing_embed.add_field(name='Location', value=self.location, inline=True)
        listing_embed.add_field(name='Price', value=self.price, inline=True)
        listing_embed.set_image(url=self.imageurl)
        listing_embed.set_thumbnail(url='https://www.shareicon.net/data/128x128/2016/08/18/810389_strategy_512x512.png')
        return listing_embed

def kijiji_json_parse(dictionary):
    ''' Edits the PowerShell formed Kijiji Search Result
    into useable fields for Python and end user display'''

    # Force the keys to be lowercase
    dictionary = dict((key.lower(), value) for key, value in dictionary.items())

    for key, value in dictionary.items():
        if key == 'postedasdate':
            if value is not None and 'Date' in value:
                # Extract the unix data from the string
                regex_match = re.search('\d+', value)
                # This is from PowerShell and is unix date in milliseconds
                unix_date = int(regex_match.group(0)) / 1000
                # Convert it to a EST string date
                dictionary['postedasdate'] = datetime.datetime.utcfromtimestamp(unix_date).strftime('%B %#d, %#I:%M')
    return dictionary

# Scripts running location. Only set if called via python.exe
__location__ = os.path.realpath(
    # From https://docs.python.org/3/library/os.path.html
    # If a component is an absolute path, all previous components
    # are thrown away and joining continues from the absolute path component.
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load Configuration File
config_file_name = "bot_cfg.json"
config_file_path = Path(os.path.join(__location__, config_file_name))

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
if "command_prefix" in config_options.keys():
    defined_command_prefix = config_options["command_prefix"]
    print("Using {} as a command declaration string".format(
        config_options["command_prefix"]))
else:
    print("Does not appear to be a key called 'command_prefix'. \
        Using default: {}".format(default_command_prefix))
    defined_command_prefix = default_command_prefix

bot = Bot(command_prefix=defined_command_prefix)
# Remove the built-in help command in place of an embed based one.
bot.remove_command("help")

@bot.event
async def on_ready():
    """Event for when the bot is ready to start working"""
    print("Ready when you are")
    print("I am runing on " + bot.user.name)
    print("With the id " + bot.user.id)
    await bot.change_presence(game=discord.Game(name='hard to get'))


@bot.command(pass_context=True)
async def ping(context, *args):
    """Verifcation that the bot is running and working."""
    await bot.say(":eight_spoked_asterisk: I'm here {}".format(
        context.message.author))
    # Remove the message that triggered this command
    await bot.delete_message(context.message)
    print("{} has pinged".format(context.message.author))


@bot.command(pass_context=True)
async def help(context):
    """Discord Embed to display command based help"""
    embed = discord.Embed(
        title="Help!",
        description="Basically, this is how I'm used.",
        color=0x00a0ea)
    embed.add_field(
        name="{}ping".format(config_options["command_prefix"]),
        value="Verifcation that the bot is running and working.")
    embed.add_field(
        name="{}rembed".format(config_options["command_prefix"]),
        value="Let's you embed with more user input. After entering your \
            message the bot will ask questions about the color and thumbnail.")
    embed.set_footer(text="Embed-This!")
    await bot.say(embed=embed)

async def json_trawler_task():
    await bot.wait_until_ready()
    if 'listing_path' in config_options.keys() and 'posting_channel' in config_options.keys():
        json_directory = Path(config_options["listing_path"])

        channel = discord.Object(id=config_options["posting_channel"])
        print("Channel:", channel)
        print(bot.is_closed)
        while not bot.is_closed:
            # Iterate over the children in the directory
            print('in loop')
            try:
                for childitem in list(json_directory.iterdir())[0:2]:
                    print("Working with: {}".format(childitem))
                    # Open the file and convert it from json
                    with open(childitem) as listing_file:
                        listing_options = json.load(listing_file, object_hook=kijiji_json_parse)
                        # Create a kijiji listing object
                        kijiji_listing = KijijiListing(dictionary=listing_options)
                    os.remove(childitem)
                    print(kijiji_listing.to_embed())
                    # await bot.send_message(destination=channel, embed=kijiji_listing.to_embed())
                    await bot.say(embed=kijiji_listing.to_embed())
            except OSError as error:
                print("'{}' is not a valid directory or is not accessible".format(json_directory))

            await asyncio.sleep(60)  # task runs every 60 seconds
    else:
        await bot.send_message("Missing config options 'listing_path' and/or 'posting_channel' cannot run listing background task")

# Run the bot using config token
if "token" in (config_options.keys()):
    # Run the bot with the supplied token
    bot.loop.create_task(json_trawler_task())
    bot.run(config_options["token"])
else:
    print("Does not appear to be a key called 'token'")
