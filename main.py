# import discord stuff
import glob
import os
from discord.ext.commands import Bot
from apikeys import *
from bs4 import BeautifulSoup
import asyncio
import random
from discord import player
from itertools import count
import yt_dlp
import asyncio
import json
import requests
import discord
from discord.ext import commands
from discord import app_commands
from discord.flags import Intents
from discord import FFmpegPCMAudio
from collections import deque
intents = discord.Intents.default()
Intents.voice_states = True


# import api keys

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = 73782100775415808
SONG_QUEUES = {}

# new play feature
async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))


def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)
    
    
async def play_next_song(voice_client, guild_id, channel):
    if SONG_QUEUES[guild_id]:
        audio_url, title = SONG_QUEUES[guild_id].popleft()
        
        ffmpeg_options = {
         "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
         "options": "-vn -c:a libopus -b:a 256k -ar 48000 -ac 2"
       }


        source = discord.FFmpegOpusAudio(
          audio_url, **ffmpeg_options, executable="/bin/ffmpeg")
        
        def after_play(error):
            if error:
                print(f"Error playing {title}: {error}")
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id, channel), client.loop)
        
        voice_client.play(source, after=after_play)
        asyncio.create_task(channel.send(f"Now playing: **{title}**"))
    else:
      await voice_client.disconnect()
      SONG_QUEUES[guild_id] = deque()

        
#Get free game on epic

@client.tree.command(name="free_epic", description="Check free games on EPIC game launcher")
async def free_epic(interaction: discord.Interaction):
    await interaction.response.defer()
    url = "https://free-epic-games.p.rapidapi.com/free"

    headers = {
        "X-RapidAPI-Key": RAPIDKEY,
        "X-RapidAPI-Host": "free-epic-games.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    # Parse the response text as a JSON object
    parsed_response = json.loads(response.text)

    # Access the "freeGames" field of the JSON object
    free_games = parsed_response['freeGames']

    # Access the "current" field of the "freeGames" object
    current_games = free_games['current']

    # Iterate over the list of games
    for game in current_games:
        # Print the "title" field of each game
        await interaction.followup.send(":pencil2:" + game['title'] + ":pencil2:")
        await interaction.followup.send(game['description'])


# new way to play music
@client.tree.command(name="play", description="Play a song or add it to the queue")
@app_commands.describe(song_query="Search query")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()


    voice_channel = interaction.user.voice.channel

    if voice_channel is None:
        await interaction.followup.send("You must be in a voice channel.")
        return

    voice_client = interaction.guild.voice_client
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
        "quiet": True,
        "extract_flat": False,
        'outtmpl': '/home/pi/Documents/discordbot/muzika/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    query = "ytsearch1: " + song_query
    results = await search_ytdlp_async(query, ydl_opts)
    tracks = results.get("entries", [])
    if tracks is None:
        await interaction.followup.send("No tracks found.")
        return

    first_track = tracks[0]
    audio_url = first_track["url"]
    title = first_track.get("title", "Unknown")
    
    guild_id = str(interaction.guild_id)
    if SONG_QUEUES.get(guild_id) is None:
        SONG_QUEUES[guild_id] = deque()
    
    SONG_QUEUES[guild_id].append((audio_url, title))
    
    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Added to queue: **{title}**")
    else:
        await interaction.followup.send(f"Now playing: **{title}**")
        await play_next_song(voice_client, guild_id, interaction.channel)

@client.tree.command(name="skip", description="Skips the current playing song")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")
    else:
        await interaction.response.send_message("Not playing anything to skip.")


@client.tree.command(name="pause", description="Pause the currently playing song.")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("I'm not in a voice channel.")

    # Check if something is actually playing
    if not voice_client.is_playing():
        return await interaction.response.send_message("Nothing is currently playing.")
    
    # Pause the track
    voice_client.pause()
    await interaction.response.send_message("Playback paused!")


@client.tree.command(name="resume", description="Resume the currently paused song.")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("I'm not in a voice channel.")

    # Check if it's actually paused
    if not voice_client.is_paused():
        return await interaction.response.send_message("I’m not paused right now.")
    
    # Resume playback
    voice_client.resume()
    await interaction.response.send_message("Playback resumed!")


@client.tree.command(name="stop", description="Stop playback and clear the queue.")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if not voice_client or not voice_client.is_connected():
        return await interaction.response.send_message("I'm not connected to any voice channel.")

    # Clear the guild's queue
    guild_id_str = str(interaction.guild_id)
    if guild_id_str in SONG_QUEUES:
        SONG_QUEUES[guild_id_str].clear()

    # If something is playing or paused, stop it
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    # (Optional) Disconnect from the channel
    await voice_client.disconnect()

    await interaction.response.send_message("Stopped playback and disconnected!")

@client.event
async def on_ready():
    test_guild = discord.Object(id=GUILD_ID)
    # Comment out clear_commands if you want to preserve your registered commands:
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}")
    print("Discord bot is ready to use!")

client.run(BOTTOKEN)
