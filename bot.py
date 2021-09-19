import discord
import os
from discord.ext import commands
import sys
from youtube_dl import YoutubeDL
import requests
import asyncio
import time

import urllib
import pafy
import re

#Load token from the .env file
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

#'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
FFMPEG_OPTIONS = {'before_options': '-reconnect 1', 'options': '-vn'}

#create the client
intents = discord.Intents().all()
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$',intents=intents)

#display a message to console when the bot connects
@bot.event
async def on_ready():
    print("Logged on as {0}!".format(bot.user))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Command not found")

#simple echo test command
@bot.command()
async def echo(ctx):
    await ctx.send(ctx.message.content[5::])

#Get videos from links or from youtube search
def search(arg):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(arg)
        except: info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else: info = ydl.extract_info(arg, download=False)
    return (info['title'], info['formats'][0]['url'])

#join a voice channel and play music
@bot.command()
async def play(ctx):
    if not ctx.voice_client:
        await ctx.send("Not in a voice channel, please use $join")
        return

    title, url = search(ctx.message.content[5::])

    #play the music
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client
        audio_source = discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS, stderr=sys.stdout)
        #async with ctx.typing():
        voice_channel.play(audio_source, after=lambda e: print('Done playing'))
        await ctx.send('Now playing: {}'.format(title))
        if voice_channel.is_playing():
            print("playing music")
        else:
            print("AHHHH BAD")
    except Exception as e:
        print(e)
        await ctx.send("I am having some issues playing: {}".format(title))
        return

#join a voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice == None or ctx.author.voice.channel == None:
        return        
    channel = ctx.message.author.voice.channel
    await channel.connect()

#leave voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        return

@bot.command()
async def test(ctx):

    search = ctx.message.content[5::]

    if ctx.message.author.voice == None:
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    channel = ctx.message.author.voice.channel

    voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)

    voice_client = None

    if voice_client == None:
        voice_client = await voice.connect()
    else:
        await voice_client.move_to(channel)

    search = search.replace(" ", "+")

    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        
    await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])

    song = pafy.new(video_ids[0])  # creates a new pafy object

    audio = song.getbestaudio()  # gets an audio source

    source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use

    voice_client.play(source)  # play the source

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)