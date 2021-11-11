import discord
from discord.ext import commands

#TODO
# ADDED TEST FUNCTIONALITY
# WOULDNT IT BE COOL IF IT WAS SOMEHOW ABLE TO TEST ITSELF?????
# APART FROM POSSIBLE COOLNESS THIS IS WHERE GENERIC COMMANDS WOULD GO, AS OF YET THOSE ARE UNKNOWN

#TODO
# IMPLEMENT CLEAR CHANNEL COMMANDS
# THIS WILL CLEAR ALL PREVIOUS MESSAGE IN A TEXT CHANNEL NAMED MUSIC
# MAKE THIS ONLY CALLABLE BY SERVER OWNER??? WILL NEED PERMISSIONS

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command()
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[5::])