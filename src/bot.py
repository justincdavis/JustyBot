import asyncio
import time

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands.bot import when_mentioned_or

from .classes import CommandQueue
from .cogs import Events, Music, Utility


class Bot:
    def __init__(self):
        self._intents = discord.Intents().all()
        self._bot = commands.Bot(
            command_prefix=when_mentioned_or("$"), intents=self._intents
        )
        self._commands: CommandQueue = CommandQueue()

        cogs = [Events, Music, Utility]
        for cog in cogs:
            cog = cog(self._bot, self._commands)
            self._commands.put(self._bot.add_cog, cog)

    def run(self, token: str):
        self._bot.run(token)
