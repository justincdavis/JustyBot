import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged on as {0}!".format(self.bot.user))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            print("Command not found: {}".format(ctx.message.content))
            await ctx.send("Command not found: {}".format(ctx.message.content[0:6]))
        else:
            print("Command error on message: {} \n With error: {}".format(ctx.message.content, error))