#!/usr/bin/python3
import sys
import os
import asyncio

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ModuleNotFoundError:
    pass

from dotenv import load_dotenv

from .src import Bot

# loads the discord token from the .env
def get_discord_token():
    load_dotenv()
    return os.getenv("DISCORD_TOKEN")


if __name__ == "__main__":
    # Add the extern folder to the path
    # for finding the packaged ffmpeg
    sys.path.insert(0, "./extern")

    bot = Bot()
    bot.run(get_discord_token())
