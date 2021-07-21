# import discord stuff
import discord
from discord.ext import commands
from discord.flags import Intents
from discord import FFmpegPCMAudio
import requests
import json
import youtube_dl
import os, glob
from itertools import count
from discord import player
import random
import asyncio

# import api keys
from apikeys import *

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '!', intents=intents)


queues = {}
def ytdownload(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/home/pi/Documents/discordbot/muzika/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            #os.rename(file, "song.mp3")
            songextname = file
            songname = os.path.splitext(songextname)[0]
            return songextname


def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source)

@client.event
async def on_ready():
    print ("Discord bot is ready to use!")
    print ("-----------------------------")

# Says Hello
@client.command()
async def hello(ctx):
    await ctx.send("Hello I am the WhitKnight! I am your master!")

# Prints joke
@client.command()
async def joke(ctx):
    url = "https://dad-jokes.p.rapidapi.com/random/joke"
    headers = {
        'x-rapidapi-key': JOKEAPI,
        'x-rapidapi-host': "dad-jokes.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)
    await ctx.send(json.loads(response.text)['body'][0]['setup'])
    await ctx.send(json.loads(response.text)['body'][0]['punchline'])

@client.command()
async def insult(ctx, name=None):
    url = "https://evilinsult.com/generate_insult.php"
    response = requests.request("GET", url)
    if name is None:
        await ctx.send(response.text)
    else:
        await ctx.send(name + ", " + response.text)

#Bot join voice channel
@client.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        #Play audio from local storage
        #source = FFmpegPCMAudio('rasputin.mp3')
        #player = voice.play(source)
        await ctx.send ("I have come my slavers prais me!")
    else:
        await ctx.send("You are not in a voice channel peasant, you must be in a voice channel you stupid fool!")

# Bot leave voice channel
@client.command(pass_context = True, aliases=['l', 'exit'])
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send ("I am leaving this wretched voice channel!")
    else:
        await ctx.send("I am not in a fucking voice channel!")

#Pause music that is  playing
@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Fuck you!, I am not playing any music at the moment, play some song first!")

#Resume music
@client.command(pass_context = True, aliases=['c'])
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("You fool no song is paused!")

@client.command(pass_context = True, aliases=['s'])
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    voice.stop()

#play <music_name>_ by downloading youtube
""" @client.command(pass_context = True, aliases=['p', 'yt'])
async def play(ctx, url:str):
    #song_there = os.path.isfile("*.mp3")
    try:
        #for deletemp3 in glob.glob("/home/pi/Documents/discordbot/muzika/*.mp3"):
        for deletemp3 in glob.glob("*.mp3"):
            os.remove(deletemp3)
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the '!stop' command")
        return

    channel = ctx.message.author.voice.channel
    voice = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        #'outtmpl': '/home/pi/Documents/discordbot/muzika/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    #for file in os.listdir("/home/pi/Documents/discordbot/muzika/"):
    for file in os.listdir("./."):
        if file.endswith(".mp3"):
            #os.rename(file, "song.mp3")
            songextname = file
            songname = os.path.splitext(songextname)[0]
    source = FFmpegPCMAudio(songextname)
    player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id)) """

# play withouth downloading 
@client.command(pass_context = True, aliases=['p', 'yt'])
async def play(ctx, url: str):
    video_link = url
    ydl_opts = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()

    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_link, download=False)
        URL = info['formats'][0]['url']
    voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    while voice.is_playing(): #Checks if voice is playing
        await asyncio.sleep(1) #While it's playing it sleeps for 1 second
    else:
        await asyncio.sleep(15) #If it's not playing it waits 15 seconds
    while voice.is_playing(): #and checks once again if the bot is not playing
        break #if it's playing it breaks
    else:
        await voice.disconnect() #if not it disconnects
@client.command(pass_context = True, aliases=['q', 'que'])
async def queue(ctx, url:str):
    voice = ctx.guild.voice_client
    song = (ytdownload(url))
    source = FFmpegPCMAudio(song)
    guild_id = ctx.message.guild.id
    if guild_id in queues:
        queues[guild_id.append(source)]
    else:
        queues[guild_id] = [source]
    await ctx.send("Added to queue: " + song)

@client.command(pass_context = True, aliases=['r'])
async def radio(ctx, radio:str = None):
    channel = ctx.message.author.voice.channel
    if radio == 'mreznica':
      player = await channel.connect()
      player.play(FFmpegPCMAudio('https://stream3.dns69it.com:443/stream'))
    elif radio == 'otvoreni':
      player = await channel.connect()
      player.play(FFmpegPCMAudio('https://stream.otvoreni.hr:443/otvoreni'))
    elif radio == 'extrafm':
      player = await channel.connect()
      player.play(FFmpegPCMAudio('http://streams.extrafm.hr:8110/stream'))
    elif radio == 'antena':
      player = await channel.connect()
      player.play(FFmpegPCMAudio('http://live.antenazagreb.hr:8000/stream'))
    if radio is None:
        await ctx.send("You did not specify radio, type !r [mreznica, otvoreni, extrafm, antena]")

player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

@client.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

client.run(BOTTOKEN)
