import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


dc_intents = discord.Intents.all()
dc_bot = commands.Bot(command_prefix = '!', intents=dc_intents, application_id=1194325058882126005)

async def join_voice_channel(client: discord.Client, voice_channel: discord.VoiceChannel, cls=None) -> discord.VoiceProtocol:
    if client.voice_clients is not None:
        for voice_client in client.voice_clients:
            if voice_client.channel == voice_channel:
                return voice_client
    if cls:
        return await voice_channel.connect(cls=cls)
    else:
        return await voice_channel.connect()

async def leave_voice_channel(
    client: discord.Client, voice_channel: discord.VoiceChannel
):
    for voice_client in client.voice_clients:
        if voice_client.channel == voice_channel:
            return await voice_client.disconnect()

async def init_load_all_cog():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await dc_bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
    asyncio.run(init_load_all_cog())
    bot_token = os.environ.get("discord_bot_token")
    dc_bot.run(bot_token)