import discord
from discord.ext import commands
from discord.ext.commands.bot import when_mentioned_or
from discord.ext.commands.errors import CommandError
from classes import song_queue
from classes.song_queue import Song,Song_Queue,get_song_youtube
import sys
import asyncio

#TODO
# REFACTOR INTO BACKEND FRONTEND METHODS
# CHANGE PLAY TO USE THE DIFFERENT PLAY TYPES (SOUNDCLOUD, SPOTIFY, YOUTUBE) AND MAKE A DETERMINATION FROM THE DEFAULT MODE
# WHENVER TEXT IS BEING SENT TO DISCORD ABSTRACT THAT TO ANOTHER METHOD
# ALLOWS MAKING THE TEXT PRETTIER TO BE EASIER
# SAVE A QUEUE OF MESSAGE OUTPUT THAT THE BOT CAN CLEANUP TO NOT MAKE THE CHANNEL AS MESSY
# AUTO CLEANUP SHOULD DELETE MESSAGE QUERIES AND DELETE QUEUED STATUS 

#GLOBAL OPTIONS
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#bot class to handle all commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.song_queue = Song_Queue([])
        self.current_song = None
        self.current_voice_ctx = None
        self.last_command = None

    def update_ctx(self, ctx):
        if ctx != None:
            self.current_voice_ctx = ctx
        return self.current_voice_ctx

    def update_last_command(self, com):
        self.last_command = com

    def get_next_song(self):
        return self.song_queue.get_next_song()

    async def add_song(self, ctx, search):
        song = get_song_youtube(search)
        url, title, artist, duration, youtube_url = song.get_all_data()
        if(ctx.guild.voice_client.is_playing()):
            await ctx.send('{} by {} has been added to the queue'.format(title, artist, duration))
            await ctx.send(youtube_url)
        self.song_queue.add_song(get_song_youtube(search))

    async def play_next_song(self, ctx):
        ctx = self.update_ctx(ctx)
        ctx.guild.voice_client.resume()
        song = self.get_next_song()
        self.current_song = song
        if(song != None):
            url, title, artist, duration, youtube_url = song.get_all_data()
        else:
            ctx.guild.voice_client.stop()
            await ctx.send("No more songs in the queue")
            return
        async with ctx.typing(): 
            source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
            try:
                ctx.voice_client.play(source, after = self.finished_song)
            except Exception as e:
                raise e
            await ctx.send('Now playing: {} by {}, {} seconds'.format(title, artist, duration))
            await ctx.send(youtube_url)

    def finished_song(self, ctx):
        if self.last_command == self.stop:
            return
        else:
            coro = self.play_next_song(self.current_voice_ctx)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

    @commands.command()
    async def join(self, ctx):
        self.update_last_command(self.join)
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            await ctx.send("User is not in a voice channel")
            raise CommandError("User is not in a voice channel")      
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        self.update_last_command(self.leave)
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot not connected to a voice channel")
            raise CommandError("Bot not connected to a voice channel")  

    @commands.command()
    async def stop(self, ctx):
        self.update_last_command(self.stop)
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            await ctx.send("Stopped playing: {}".format(self.current_song.get_title()))

    @commands.command()
    async def skip(self, ctx):
        self.update_last_command(self.skip)
        if ctx.guild.voice_client.is_playing():
            await self.stop(ctx)
            await self.play_next_song(ctx)
        elif (ctx.voice_client and self.song_queue.get_num_songs() > 0):
            await self.play_next_song(ctx)
        else:
            await ctx.send("Not playing any music")
            raise CommandError("Not playing any music")  

    @commands.command()
    async def pause(self, ctx):
        self.update_last_command(self.pause)
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.pause()
            await ctx.send("Paused the music player")
        elif ctx.guild.voice_client.is_paused():
            await self.resume(ctx)

    @commands.command()
    async def unpause(self, ctx):
        self.update_last_command(self.unpause)
        await self.resume(ctx)

    @commands.command()
    async def resume(self, ctx):
        self.update_last_command(self.resume)
        if ctx.guild.voice_client.is_paused():
            ctx.guild.voice_client.resume()
            await ctx.send("Unpaused the music player")
        if self.song_queue.get_num_songs() > 0 and self.last_command == self.stop:
            await self.play_next_song(ctx)

    @commands.command()
    async def play(self, ctx):
        # self.update_last_command(self.play)
        # if ctx.guild.voice_client:
        #     if (len(ctx.message.content) > 6):
        #         await self.add_song(ctx, ctx.message.content[5::])
        #     else:
        #         if (ctx.guild.voice_client.is_paused()):
        #             await self.resume(ctx)
        #         elif (not ctx.guild.voice_client.is_playing() and self.song_queue.get_num_songs() > 0):
        #             await self.play_next_song(ctx)
        #         else:
        #             await ctx.send("Please provide a song to play")
        # else:
        #     try:
        #         await self.join(ctx)
        #         await self.add_song(ctx, ctx.message.content[5::])
        #         await self.play_next_song(ctx)
        #     except Exception as e:
        #         raise e
        self.update_last_command(self.play)
        if ctx.guild.voice_client:
            if (len(ctx.message.content) > 6):
                await self.add_song(ctx, ctx.message.content[5::])
            else:
                if (ctx.guild.voice_client.is_paused()):
                    await self.resume(ctx)
                elif (not ctx.guild.voice_client.is_playing() and self.song_queue.get_num_songs() > 0):
                    await self.play_next_song(ctx)
                else:
                    await ctx.send("Please provide a song to play")
        else:
            try:
                await self.join(ctx)
                await self.add_song(ctx, ctx.message.content[5::])
                await self.play_next_song(ctx)
            except Exception as e:
                raise e

    @commands.command()
    async def queue(self, ctx):
        await ctx.send(song_queue.print_discord())

#TAKE A YOUTUBE LINK TO PLAY
#REMOVE LAST SONG FROM QUEUE