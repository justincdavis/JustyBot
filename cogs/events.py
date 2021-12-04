import discord
from discord.ext import commands

#TODO
# WANT TO INTEGRATE CUSTOM EVENTS????? IS THIS POSSIBLE IN DISCORD.PY
# EVERY TYPE OF EVENT SHOULD REALLY BE HANDLED IN HERE EVEN IF IT IS JUST A RETURN

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged on as {0}!".format(self.bot.user))
        await self.bot.change_presence(activity=discord.Game(name='$help'))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            print("Command not found: {}".format(ctx.message.content))
            # not quite what should be here for command error (slice on ' ' and take first element), not [0:6]
            await ctx.send("Command not found: {}".format(ctx.message.content[0:6]))
        else:
            print("Command error on message: {} \n With error: {}".format(ctx.message.content, error))