import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands.bot import when_mentioned_or


class Bot:
    def __init__(self):
        self._intents = discord.Intents().all()
        self._bot = commands.Bot(
            command_prefix=when_mentioned_or("$"), intents=self._intents
        )

        cogs = [t for t in cogs if isinstance(t, Cog)]
        for cog in cogs:
            self._bot.add_cog(cog)

    def run(self, token: str):
        self._bot.run(token)
