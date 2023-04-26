import discord
from discord.ext import commands

from ..classes import CommandQueue


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot, queue: CommandQueue) -> "Events":
        self._bot: commands.Bot = bot
        self._queue: CommandQueue = queue

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self._bot.user}!")
        await self._bot.change_presence(activity=discord.Game(name="$help"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.errors.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            print("Command not found: {}".format(ctx.message.content))
            command = ctx.message.content.split()[0]
            await ctx.send("Command not found: {}".format(command))
        else:
            print(
                "Command error on message: {} \n With error: {}".format(
                    ctx.message.content, error
                )
            )
