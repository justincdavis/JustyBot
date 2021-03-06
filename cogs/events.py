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
            command = ctx.message.content.split()[0]
            await ctx.send("Command not found: {}".format(command))
        else:
            print("Command error on message: {} \n With error: {}".format(ctx.message.content, error))
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            #await channel.send("Welcome {0.mention}.".format(member))
            print("Welcome {}.".format(member))