import asyncio
import datetime
import re
import discord
import wavelink
from discord.ext import commands
from main import join_voice_channel

YOUTUBE_PLAYLIST_REGEX = re.compile(r'(?:list=)([a-zA-Z0-9_-]+)')


class WavelinkHandler:

    def __init__(self, client: discord.Client):
        self.client = client
        self.pool: wavelink.Pool = wavelink.Pool()
        self.player: wavelink.Player = None
        self.volume: int = 50
        self.isAutoPlay : bool = False

    async def connect(self):
        node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass',)
        await self.pool.connect(client=self.client, nodes=[node])

        for node_id, node in self.pool.nodes.items():
            print(f'✅ Node: {node_id} | Object: {node}')

    async def joinChannel(self, client: discord.Client, voice_channel: discord.VoiceChannel):
        self.player: wavelink.Player = await join_voice_channel(client, voice_channel, cls=wavelink.Player)

    async def playMusic(self, ctx: commands.Context, youtube_url: str, is_interruption: bool):
        if self.player == None:
            await ctx.send('❌ 播放功能錯誤！')
            return
        
        self.player.autoplay = wavelink.AutoPlayMode.enabled if self.isAutoPlay else wavelink.AutoPlayMode.disabled
        tracks: wavelink.Search = await wavelink.Playable.search(youtube_url)
        is_playlist = bool(YOUTUBE_PLAYLIST_REGEX.search(youtube_url))

        if not tracks:
            await ctx.send('❌ 找不到音樂！')
            return

        #Filter while isn't a play list but tracks count > 1
        if (is_playlist is False):
            tracks = [tracks[0]]

        message = ''
        for index, track in enumerate(tracks):
            if (is_interruption is True):
                self.player.queue.put_at(index, track)
                message += f'已將 ***{track.title}*** 插入播放清單\n'
            else:
                self.player.queue.put(track)
                message += f'已將 ***{track.title}*** 加入播放清單\n'
        await ctx.reply(f'{message}')
        
        if (self.player.playing is False):
            first_track = self.player.queue.get_at(0)
            await self.player.play(first_track, volume=self.volume)

    async def skipMusic(self):
        return await self.player.skip()

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

#lavalink Event Reference from MusicCommands
    async def on_wavelink_player_update(self, payload: wavelink.PlayerUpdateEventPayload):
        print('on_wavelink_player_update')
        
        
    async def on_wavelink_track_start(self, payload: wavelink.NodeReadyEventPayload):
        print(f'[{datetime.now()}] on_wavelink_track_start: {payload.track.title}')


    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload):
        print(f'[{datetime.now()}] on_wavelink_track_end: {payload.track.title}')
        if (self.player.playing is False) and (self.player.queue.count > 0):
            first_track = self.player.queue.get_at(0)
            await self.player.play(first_track, volume=self.volume)
            return True
        else:
            return False