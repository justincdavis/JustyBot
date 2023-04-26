from discord.ext import commands

from ..classes import CommandQueue


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot, queue: CommandQueue) -> "Utility":
        self._bot: commands.Bot = bot
        self._queue: CommandQueue = queue

    @commands.command()
    async def echo(self, ctx: commands.Context):
        await ctx.send(ctx.message.content[5::])

    @commands.command()
    async def sourcecode(self, ctx: commands.Context):
        await ctx.send(
            "Here is my source code:\nhttps://github.com/justincdavis/JustyBot"
        )
