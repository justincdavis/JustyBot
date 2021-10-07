import discord
from discord.ext import commands
from discord.ext.commands.bot import when_mentioned_or
from classes.song_queue import Song,Song_Queue,get_song_youtube
import sys

#GLOBAL OPTIONS
FFMPEG_OPTIONS = {'before_options': '-reconnect 1', 'options': '-vn'}

#bot class to handle all commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = Song_Queue([])

    def get_next_song(self):
        return self.song_queue.get_next_song()

    def add_song(self, search):
        self.song_queue.add_song(get_song_youtube(search))

    async def play_next_song(self, ctx):
        song = self.get_next_song()
        if(song != None):
            url, title, artist, duration = song.get_all_data()
        else:
            return
        async with ctx.typing():  
            source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
            ctx.voice_client.play(source, after = self.check_queue())
        await ctx.send('Now playing: {} by {}, {} seconds'.format(title, artist, duration))

    def check_queue(self):
        if(self.song_queue.get_num_songs() > 0):
            print("I should play another song")

    @commands.command
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[5::])

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            await ctx.send("User is not in a voice channel")
            raise commands.CommandError("User is not in a voice channel")      
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot not connected to a voice channel")
            raise commands.CommandError("Bot not connected to a voice channel")  

    @commands.command()
    async def stop(self, ctx):
        await self.leave(ctx)

    @commands.command()
    async def skip(self, ctx):
        if ctx.guild.voice_client:
            await self.play_next_song(ctx)
        else:
            raise commands.CommandError("Not playing any music")  

    @commands.command()
    async def play(self, ctx):
        if(ctx.guild.voice_client):
            self.add_song(ctx.message.content[5::])
        else:
            try:
                await self.join(ctx)
                self.add_song(ctx.message.content[5::])
                await self.play_next_song(ctx)
            except Exception as e:
                raise e

#change stop to stop the voice broadcast player
#change leave to do stop and then disconnnect
#change skip to add await stop then play_next