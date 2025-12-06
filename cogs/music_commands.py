import discord
import wavelink
from discord.ext import commands
from lib.handler.wavelink_handler import WavelinkHandler


class MusicCommands(commands.Cog):

    def __init__(self, client=discord.Client):
        self.client = client
        self.wavelink_handler : WavelinkHandler = WavelinkHandler(self.client)
        self.playing_channel : discord.StageChannel = None
        self.text_channel : discord.TextChannel = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.wavelink_handler.connect()

    @commands.hybrid_command(name='kiki放音樂', help='kiki會幫你放音樂')
    async def play_music(self, ctx: commands.Context, 網址: str, 插播: bool):
        if (ctx.author.voice is not None):
            target_channel = ctx.author.voice.channel
            if (target_channel != self.playing_channel):
                await ctx.defer()
                await self.wavelink_handler.joinChannel(client=self.client, voice_channel=target_channel)
                await ctx.channel.send(f'***kiki來***{ctx.author.voice.channel}***放音樂了***')
            else:
                await ctx.defer()
            self.playing_channel = target_channel
            self.text_channel = ctx.channel
            await self.wavelink_handler.playMusic(ctx, 網址, 插播)          
        else:
            await ctx.send('**kiki不知道該去哪放音樂**')

    @commands.hybrid_command(name='kiki切歌', help='kiki會幫你切歌')
    async def stop_music(self, ctx: commands.Context):
        await ctx.defer()
        track = await self.wavelink_handler.skipMusic()
        if (track is not None):
            await ctx.send(f'kiki把 ***{track.title}*** 切掉了')
        else:
            await ctx.send('沒有歌可以切餒')

    @commands.hybrid_command(name='調整音樂音量', help='可以調整音量大小(0-100)')
    async def set_volume(self, ctx: commands.Context, 音量: int):
        await ctx.defer()
        if 音量 < 0 or 音量 > 100:
            await ctx.send(f'**{音量}** ??? 有人在皮喔')
            return
        
        await self.wavelink_handler.setVolume(音量)
        if 音量 > 0:
            await ctx.send(f'已調整音樂音量: {音量}')
        else:
            await ctx.send(f'**kiki閉嘴了**')

    @commands.hybrid_command(name='設定自動播放', help='可以設定要不要隨機自動播放下一首歌')
    async def set_auto_play(self, ctx: commands.Context, 自動播放: bool):
        await ctx.defer()
        await self.wavelink_handler.setAutoPlay(自動播放)
        await ctx.send(f'已設定自動播放: {自動播放}')

    @commands.hybrid_command(name='查看播放清單', help='看播放清單裡的歌')
    async def get_play_list(self, ctx: commands.Context):
        await ctx.defer()
        if (self.wavelink_handler.player is not None) and (self.wavelink_handler.player.queue.count > 0):
            queue = self.wavelink_handler.player.queue
            play_list = ''
            for index in range(queue.count):
                track = queue.peek(index)
                play_list += f'{track.title}\n'
            await ctx.send(f'{play_list}')
        else:
            await ctx.send('沒歌了')

#lavalink Event Reference
    @commands.Cog.listener()
    async def on_wavelink_player_update(self, payload: wavelink.PlayerUpdateEventPayload):
#        await self.wavelink_handler.on_wavelink_player_update(payload)
        seconds = int(payload.position / 1000)
#        time = f'{seconds/60}:{seconds%60}'
#        custom_activity = discord.CustomActivity(f'🎵 {track.title}')
#        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)
        
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.NodeReadyEventPayload):
        await self.wavelink_handler.on_wavelink_track_start(payload)
        track = payload.track
        await self.text_channel.send(f'🎶 現在播放：{track.title}\n{track.uri}')
        custom_activity = discord.CustomActivity(f'🎵 {track.title}')
        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload):
        if (await self.wavelink_handler.on_wavelink_track_end(payload) is False):
            custom_activity = discord.CustomActivity('喵喵')
            await self.client.change_presence(status=discord.Status.online, activity=custom_activity)

async def setup(command_bot: commands.Bot):
    await command_bot.add_cog(MusicCommands(command_bot))
