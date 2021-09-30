import discord
from discord.ext import commands
from discord.ext.commands.bot import when_mentioned_or
from classes.song_queue import Song,Song_Queue

#bot class to handle all commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = Song_Queue([])
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1', 'options': '-vn'}
    def get_next_song(self):
        if(len(self.song_queue) > 0):
            return self.song_queue[0].get_title()

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            return        
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
        else:
            return

    @commands.command()
    async def stop(self, ctx):
        self.leave(ctx)

# #display a message to console when the bot connects
# @bot.event
# async def on_ready():
#     print("Logged on as {0}!".format(bot.user))

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.CommandNotFound):
#         await ctx.send("Command not found")

# #simple echo test command
# @bot.command()
# async def echo(ctx):
#     await ctx.send(ctx.message.content[5::])

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