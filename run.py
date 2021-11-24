import discord
from discord.ext import commands
from discord.ext.commands.bot import when_mentioned_or
from dotenv import load_dotenv
import os
import sys
from cogs import events, music, utility

#creates the bot
def create_bot():
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=when_mentioned_or('$'),intents=intents)
    return bot

#add command cog
def add_command_cogs(bot, cogs):
    for cog in cogs:
        bot.add_cog(cog)

#loads the discord token from the .env
def get_discord_token():
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')

if __name__ == "__main__":
     args = sys.argv[1:]
    bot = create_bot()
    cogs = [events.Events(bot), music.Music(bot), utility.Utility(bot)]
    add_command_cogs(bot, cogs)
    bot.run(get_discord_token())
