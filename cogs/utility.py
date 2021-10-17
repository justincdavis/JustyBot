import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command()
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[5::])