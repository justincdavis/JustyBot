import discord
import os
from discord.ext import commands
import youtube_dl
import asyncio

#Load token from the .env file
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

#create the client
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$',intents=intents)

#############################################
#DEFINITIONS FOR THE YOUTUBE_DL
#from https://python.land/build-discord-bot-in-python-that-plays-music
#also found in the docs for youtube_dl
#############################################
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

#############################################
#END DEFINITIONS FOR THE YOUTUBE_DL
#############################################

#display a message to console when the bot connects
@bot.event
async def on_ready():
    print("Logged on as {0}!".format(bot.user))

#simple echo test command
@bot.command()
async def echo(ctx):
    await ctx.send(ctx.message.content[5::])

#join voice channel
@bot.command()
async def play(ctx):
    #connect to the voice channel
    if ctx.author.voice == None or ctx.author.voice.channel == None:
        return        
    channel = ctx.message.author.voice.channel
    await channel.connect()



    try :
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        return

#leave voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        return

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)