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

    async def play_next_song(self, ctx):
        song = self.get_next_song()
        if(song != None):
            url = self.get_next_song()
        else:
            raise commands.CommandError("No songs in the queue")
        source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

    @commands.command
    async def echo(self, ctx):
        await ctx.send(ctx.message.content[5::])

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            raise commands.CommandError("User is not in a voice channel")      
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            raise commands.CommandError("Not connected to a voice channel")  

    @commands.command()
    async def stop(self, ctx):
        self.leave(ctx)

    @commands.command()
    async def skip(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            self.play_next_song(ctx)
        else:
            raise commands.CommandError("Not playing any music")  

# #join a voice channel and play music
# @bot.command()
# async def play(ctx):
#     if not ctx.voice_client:
#         await ctx.send("Not in a voice channel, please use $join")
#         return

#     title, url = search(ctx.message.content[5::])

#     #play the music
#     try :
#         server = ctx.message.guild
#         voice_channel = server.voice_client
#         audio_source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
#         async with ctx.typing():
#             voice_channel.play(audio_source, after=lambda e: print('Done playing'))
#         await ctx.send('Now playing: {}'.format(title))
#         if voice_channel.is_playing():
#             print("playing music")
#         else:
#             print("AHHHH BAD")
#     except Exception as e:
#         print(e)
#         await ctx.send("I am having some issues playing: {}".format(title))
#         return

# #join a voice channel
# @bot.command()
# async def join(ctx):
#     if ctx.author.voice == None or ctx.author.voice.channel == None:
#         return        
#     channel = ctx.message.author.voice.channel
#     await channel.connect()

# #leave voice channel
# @bot.command()
# async def leave(ctx):
#     if ctx.voice_client:
#         await ctx.guild.voice_client.disconnect()
#     else:
#         return

# if __name__ == "__main__":
#     bot.run(DISCORD_TOKEN)