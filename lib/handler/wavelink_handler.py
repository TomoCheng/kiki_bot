import asyncio
import re
import discord
import wavelink
from discord.ext import commands
from main import join_voice_channel

YOUTUBE_PLAYLIST_REGEX = re.compile(r"(?:list=)([a-zA-Z0-9_-]+)")


class WavelinkHandler:

    def __init__(self, client: discord.Client):
        self.client = client
        self.pool: wavelink.Pool = wavelink.Pool()
        self.player: wavelink.Player = None
        self.volume: int = 50
        self.isAutoPlay : bool = False

    async def connect(self):
        node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass",)
        await self.pool.connect(client=self.client, nodes=[node])

        for node_id, node in self.pool.nodes.items():
            print(f"✅ Node: {node_id} | Object: {node}")

    async def joinChannel(self, client: discord.Client, voice_channel: discord.VoiceChannel):
        self.player: wavelink.Player = await join_voice_channel(client, voice_channel, cls=wavelink.Player)

    async def playMusic(self, ctx: commands.Context, youtube_url: str):
        if self.player == None:
            return
        
        self.player.autoplay = wavelink.AutoPlayMode.enabled if self.isAutoPlay else wavelink.AutoPlayMode.disabled
        tracks: wavelink.Search = await wavelink.Playable.search(youtube_url)
        is_playlist = bool(YOUTUBE_PLAYLIST_REGEX.search(youtube_url))
    
        if is_playlist:  ##清單
            if not tracks:
                await ctx.channel.send("❌ 找不到音樂！")
                return

            for track in tracks:
                await self.player.play(track, volume=self.volume)
                await ctx.channel.send(f"🎶 現在播放：{track.title}\n{track.uri}")
                while self.player.playing == True:
                    await asyncio.sleep(1)
                
        else:
            tracks: wavelink.Search = await wavelink.Playable.search(youtube_url)
            ##print("searching:", youtube_url)
            ##results = await wavelink.Playable.search(youtube_url)
            print("results:", tracks)

            if not tracks:
                await ctx.channel.send("❌ 找不到音樂！")
                return

            track = tracks[0]
            await self.player.play(track, volume=self.volume)
            await ctx.channel.send(f"🎶 現在播放：{track.title}\n{track.uri}")

    async def setVolume(self, volume):
        self.volume = volume
        if self.player == None:
            return
        else:
            await self.player.set_volume(self.volume)

    async def setAutoPlay(self, is_auto_play):
        self.isAutoPlay = is_auto_play
        if self.player == None:
            return
        else:
            self.player.autoplay = wavelink.AutoPlayMode.enabled if self.isAutoPlay else wavelink.AutoPlayMode.disabled