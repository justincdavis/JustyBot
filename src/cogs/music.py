import sys
import asyncio
import time
from typing import Optional, List
from functools import partial

import discord
from discord.ext import commands, tasks
from discord.ext.commands.errors import CommandError

from classes import Song, SongQueue, CommandQueue
from utils.youtube import get_song_youtube


# TODO
# REFACTOR INTO BACKEND FRONTEND METHODS
# CHANGE PLAY TO USE THE DIFFERENT PLAY TYPES (SOUNDCLOUD, SPOTIFY, YOUTUBE) AND MAKE A DETERMINATION FROM THE DEFAULT MODE
# WHENVER TEXT IS BEING SENT TO DISCORD ABSTRACT THAT TO ANOTHER METHOD
# ALLOWS MAKING THE TEXT PRETTIER TO BE EASIER
# SAVE A QUEUE OF MESSAGE OUTPUT THAT THE BOT CAN CLEANUP TO NOT MAKE THE CHANNEL AS MESSY
# AUTO CLEANUP SHOULD DELETE MESSAGE QUERIES AND DELETE QUEUED STATUS

# GLOBAL OPTIONS


# bot class to handle all commands
class Music(commands.Cog):
    """
    Class for playing music
    """

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self, bot: commands.Bot) -> "Music":
        self._bot: commands.Bot = bot
        self._song_queue: SongQueue = SongQueue()
        self._message_queue: CommandQueue = CommandQueue()

        self._current_song: Optional[Song] = None
        self._current_voice_ctx: Optional[commands.Context] = None

    def _update_ctx(self, ctx: commands.Context) -> commands.Context:
        if ctx is not None:
            self._current_voice_ctx = ctx
        return self._current_voice_ctx

    def get_next_song(self) -> Optional[Song]:
        return self._song_queue.get_next_song()

    def add_song(self, ctx: commands.Context, search) -> None:
        song: Song = get_song_youtube(search)
        _, title, artist, duration, webpage_url = song.get_all_data()
        if ctx.guild.voice_client.is_playing():
            self._message_queue.put_message(
                ctx,
                [
                    "`{} by {} has been added to the queue`".format(
                        title, artist, duration
                    ),
                    webpage_url,
                ],
            )
        self._song_queue.add_song(get_song_youtube(search))

    def play_next_song(self, ctx: commands.Context) -> None:
        ctx = self._update_ctx(ctx)
        ctx.guild.voice_client.resume()
        song = self.get_next_song()
        self.current_song = song
        if song is None:
            ctx.guild.voice_client.stop()
            self._message_queue.put_message(ctx, ["`No more songs in the queue`"])
            return
        url, title, artist, duration, webpage_url = song.get_all_data()
        source = discord.FFmpegPCMAudio(
            source=url, **Music.FFMPEG_OPTIONS, stderr=sys.stdout
        )
        try:
            ctx.voice_client.play(source, after=self.play_next_song)
        except Exception as e:
            raise e
        self._message_queue.put_message(
            ctx,
            [
                "`Now playing: {} by {}, {} seconds`".format(title, artist, duration),
                webpage_url,
            ],
        )

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            async with ctx.typing():
                await ctx.send("`User is not in a voice channel`")
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx: commands.Context):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            async with ctx.typing():
                await ctx.send("`Bot not connected to a voice channel`")
            # raise CommandError("Bot not connected to a voice channel")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            async with ctx.typing():
                await ctx.send(
                    "`Stopped playing: {}`".format(self.current_song.get_title())
                )

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if ctx.guild.voice_client.is_playing():
            await self.stop(ctx)
            await self.play_next_song(ctx)
        elif ctx.voice_client and self._song_queue.get_num_songs() > 0:
            await self.play_next_song(ctx)
        else:
            async with ctx.typing():
                await ctx.send("`Not playing any music`")
            # raise CommandError("Not playing any music")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.pause()
            async with ctx.typing():
                await ctx.send("`Paused the music player`")
        elif ctx.guild.voice_client.is_paused():
            await self.resume(ctx)

    @commands.command()
    async def unpause(self, ctx: commands.Context):
        await self.resume(ctx)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        if ctx.guild.voice_client.is_paused():
            ctx.guild.voice_client.resume()
            async with ctx.typing():
                await ctx.send("`Unpaused the music player`")
        if self.song_queue.get_num_songs() > 0 and self.last_command == self.stop:
            await self.play_next_song(ctx)

    @commands.command()
    async def play(self, ctx: commands.Context):
        if ctx.guild.voice_client:
            if len(ctx.message.content) > 6:
                await self.add_song(ctx, ctx.message.content[5::])
                if ctx.guild.voice_client.is_paused():
                    await self.resume(ctx)
                elif (
                    not ctx.guild.voice_client.is_playing()
                    and self._song_queue.get_num_songs() > 0
                ):
                    await self.play_next_song(ctx)
            else:
                if ctx.guild.voice_client.is_paused():
                    await self.resume(ctx)
                elif (
                    not ctx.guild.voice_client.is_playing()
                    and self._song_queue.get_num_songs() > 0
                ):
                    await self.play_next_song(ctx)
                else:
                    async with ctx.typing():
                        await ctx.send("Please provide a song to play")
        else:
            try:
                await self.join(ctx)
                await self.add_song(ctx, ctx.message.content[5::])
                await self.play_next_song(ctx)
            except Exception as e:
                raise e

    @commands.command()
    async def queue(self, ctx: commands.Context):
        if len(ctx.message.content) <= 6:
            async with ctx.typing():
                await ctx.send("Invalid entry in the queue for removal")
            return
        await self.add_song(ctx, ctx.message.content[6::])

    @commands.command()
    async def remove(self, ctx: commands.Context):
        index = int(ctx.message.content[7::])
        song: Optional[Song] = self._song_queue.remove_by_index(index)
        if song is None:
            async with ctx.typing():
                await ctx.send("`Invalid number in the queue entered`")
        else:
            async with ctx.typing():
                await ctx.send(
                    "`Removed: {} by {} from the queue`".format(song.title, song.artist)
                )

    @commands.command()
    async def clearqueue(self, ctx: commands.Context):
        if self._song_queue.get_num_songs() > 0:
            async with ctx.typing():
                self._song_queue.clear()
                await ctx.send("`Cleared all songs from the queue`")
        else:
            async with ctx.typing():
                await ctx.send("`Queue is empty`")

    @commands.command()
    async def viewqueue(self, ctx: commands.Context):
        async with ctx.typing():
            await ctx.send(self._song_queue.print_discord())
