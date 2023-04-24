from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> "Utility":
        self._bot: commands.Bot = bot

    @commands.command()
    async def echo(self, ctx: commands.Context):
        await ctx.send(ctx.message.content[5::])

    @commands.command()
    async def sourcecode(self, ctx: commands.Context):
        await ctx.send(
            "Here is my source code:\nhttps://github.com/justincdavis/JustyBot"
        )
