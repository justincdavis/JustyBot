import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self._bot.user}!")
        await self._bot.change_presence(activity=discord.Game(name="$help"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            print("Command not found: {}".format(ctx.message.content))
            command = ctx.message.content.split()[0]
            await ctx.send("Command not found: {}".format(command))
        else:
            print(
                "Command error on message: {} \n With error: {}".format(
                    ctx.message.content, error
                )
            )
