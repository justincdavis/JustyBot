import discord
from discord.ext import commands
from discord.ext.commands.bot import when_mentioned_or
from discord.ext.commands.errors import CommandError
from classes.song_queue import Song,Song_Queue,get_song_youtube
import sys

#GLOBAL OPTIONS
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#bot class to handle all commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.song_queue = Song_Queue([])
        self.current_song = None

    def get_next_song(self):
        return self.song_queue.get_next_song()

    async def add_song(self, ctx, search):
        song = get_song_youtube(search)
        url, title, artist, duration = song.get_all_data()
        if(ctx.guild.voice_client.is_playing()):
            await ctx.send('{} by {} has been added to the queue'.format(title, artist, duration))
        self.song_queue.add_song(get_song_youtube(search))

    async def play_next_song(self, ctx):
        if not ctx.guild.voice_client:
            ctx.guild.voice_client.resume()
        song = self.get_next_song()
        self.current_song = song
        if(song != None):
            url, title, artist, duration = song.get_all_data()
        else:
            await ctx.send("No more songs in the queue")
            return 
        async with ctx.typing(): 
            source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
            try:
                ctx.voice_client.play(source, after = self.finished_song())
            except Exception as e:
                raise e
            await ctx.send('Now playing: {} by {}, {} seconds'.format(title, artist, duration))

    def finished_song(self):
        print("song done")

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            await ctx.send("User is not in a voice channel")
            raise CommandError("User is not in a voice channel")      
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot not connected to a voice channel")
            raise CommandError("Bot not connected to a voice channel")  

    @commands.command()
    async def stop(self, ctx):
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            await ctx.send("Stopped playing: {}".format(self.current_song.get_title()))

    @commands.command()
    async def skip(self, ctx):
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
        if ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.pause()
            await ctx.send("Paused the music player")
        elif ctx.guild.voice_client.is_paused():
            await self.resume(ctx)

    @commands.command()
    async def unpause(self, ctx):
        await self.resume(ctx)

    @commands.command()
    async def resume(self, ctx):
        if ctx.guild.voice_client.is_paused():
            ctx.guild.voice_client.resume()
            await ctx.send("Unpaused the music player")

    @commands.command()
    async def play(self, ctx):
        if ctx.guild.voice_client:
            if (ctx.guild.voice_client.is_paused() and len(ctx.message.content) < 6):
                await self.resume(ctx)
            elif(len(ctx.message.content) > 6):
                await self.add_song(ctx, ctx.message.content[5::])
            else:
                await ctx.send("Please provide a song to play")
        else:
            try:
                await self.join(ctx)
                await self.add_song(ctx, ctx.message.content[5::])
                await self.play_next_song(ctx)
            except Exception as e:
                raise e