import sys
import asyncio
import time
from typing import Optional, List
from functools import partial
import atexit

import discord
from discord.ext import commands, tasks
from discord.ext.commands.errors import CommandError

from ..classes import Song, SongQueue, CommandQueue
from ..utils.youtube import get_song_youtube


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
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._message_queue: CommandQueue = CommandQueue()
        self._command_queue: CommandQueue = CommandQueue()

        self._current_song: Optional[Song] = None
        self._current_voice_ctx: Optional[commands.Context] = None

        atexit.register(self._message_queue.stop)
        atexit.register(self._command_queue.stop)

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

    def _join(self, ctx: commands.Context) -> None:
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            self._message_queue.put_message(ctx, ["`User is not in a voice channel`"])
        channel = ctx.message.author.voice.channel
        self._command_queue.put_command(channel.connect)

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        self._command_queue.put_command(partial(self._join, ctx))

    def _leave(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc:
            vc.stop()
            vc.disconnect()
        else:
            self._message_queue.put_message(ctx, ["`Bot not connected to a voice channel`"])

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        self._command_queue.put_command(partial(self._leave, ctx))

    def _stop(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc.is_playing():
            vc.stop()
            self._message_queue.put_message(
                ctx, ["`Stopped playing: {}`".format(self.current_song.get_title())]
            )

    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        self._command_queue.put_command(partial(self._stop, ctx))

    def _skip(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc.is_playing():
            self._stop()
            self.play_next_song(ctx)
        elif vc and self._song_queue.get_num_songs() > 0:
            self.play_next_song(ctx)
        else:
            self._message_queue.put_message(ctx, ["`Not playing any music`"])

    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        self._command_queue.put_command(partial(self._skip, ctx))

    def _pause(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc.is_playing():
            vc.pause()
            self._message_queue.put_message(ctx, ["`Paused the music player`"])
        elif vc.is_paused():
            self._resume(ctx)

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        self._command_queue.put_command(partial(self._pause, ctx))

    def _resume(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc.is_paused():
            vc.resume()
            self._message_queue.put_message(ctx, ["`Unpaused the music player`"])
        if self._song_queue.get_num_songs() > 0 and self.last_command == self.stop:
            self.play_next_song(ctx)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._resume, ctx))

    def _play(self, ctx: commands.Context) -> None:
        vc: discord.VoiceClient = ctx.guild.voice_client
        if vc:
            if len(ctx.message.content) > 6:
                self.add_song(ctx, ctx.message.content[5::])
                if vc.is_paused():
                    self._resume(ctx)
                elif not vc.is_playing() and self._song_queue.get_num_songs() > 0:
                    self.play_next_song(ctx)
            else:
                if vc.is_paused():
                    self._resume(ctx)
                elif not vc.is_playing() and self._song_queue.get_num_songs() > 0:
                    self.play_next_song(ctx)
                else:
                    self._message_queue.put_message(ctx, ["`Not playing any music`"])
        else:
            try:
                self._join(ctx)
                self.add_song(ctx, ctx.message.content[5::])
                self.play_next_song(ctx)
            except Exception as e:
                raise e

    @commands.command()
    async def play(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._play, ctx))

    def _queue(self, ctx: commands.Context) -> None:
        if len(ctx.message.content) <= 6:
            self._message_queue.put_message(ctx, ["`Invalid entry in the queue for removal`"])
        else:
            self.add_song(ctx, ctx.message.content[6::])

    @commands.command()
    async def queue(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._queue, ctx))

    def _remove(self, ctx: commands.Context) -> None:
        index = int(ctx.message.content[7::])
        song: Optional[Song] = self._song_queue.remove_by_index(index)
        if song is None:
            self._message_queue.put_message(ctx, ["`Invalid number in the queue entered`"])
        else:
            self._message_queue.put_message(
                ctx, ["`Removed: {} by {} from the queue`".format(song.title, song.artist)]
            )

    @commands.command()
    async def remove(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._remove, ctx))

    def _clearqueue(self, ctx: commands.Context) -> None:
        if self._song_queue.get_num_songs() > 0:
            self._song_queue.clear()
            self._message_queue.put_message(ctx, ["`Cleared all songs from the queue`"])
        else:
            self._message_queue.put_message(ctx, ["`Queue is empty`"])

    @commands.command()
    async def clearqueue(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._clearqueue, ctx))

    def _viewqueue(self, ctx: commands.Context) -> None:
        if self._song_queue.get_num_songs() > 0:
            self._message_queue.put_message(ctx, [self._song_queue.print_discord()])
        else:
            self._message_queue.put_message(ctx, ["`Queue is empty`"])

    @commands.command()
    async def viewqueue(self, ctx: commands.Context):
        self._command_queue.put_command(partial(self._viewqueue, ctx))
