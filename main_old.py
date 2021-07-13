"""
TODO
- meme sender
- yotubue 
- radio
- status of the server
- jokes
- game gambling?
"""

import discord
from discord import channel

TOKEN = ''

clien = discord.Client()

@client.event
async def on_ready():
    print ('I have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')  #Logging in terminal

    # Bot not responding to it self
    if message.author == client.user:
        return
    
    # Only in General channel
    if message.channel.name == 'General':
        if user_message.lower() == 'hello':
            await message.channel.send(f'Hello {username}')
            return
        elif user_message.lower() == 'bye': 
            await message.channel.send(f'ByeBye {username}')
            return
        
         

client.run(TOKEN)