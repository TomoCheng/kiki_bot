import discord
import wavelink
from discord.ext import commands
from lib.handler.wavelink_handler import WavelinkHandler


class MusicCommands(commands.Cog):

    def __init__(self, client=discord.Client):
        self.client = client
        self.wavelink_handler = WavelinkHandler(self.client)
        self.volume = 50

    @commands.Cog.listener()
    async def on_ready(self):
        await self.wavelink_handler.connect()

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.NodeReadyEventPayload):
        custom_activity = discord.CustomActivity(f"🎵 {payload.track.title}")
        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload):
        custom_activity = discord.CustomActivity('喵喵')
        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)

    @commands.hybrid_command(name='kiki放音樂', help='kiki會幫你放音樂')
    async def play_music(self, ctx: commands.Context, youtube_url: str):
        await ctx.defer()
        if ctx.author.voice is not None:
            await self.wavelink_handler.joinChannel(client=self.client, voice_channel=ctx.author.voice.channel)
            await ctx.send(f'***kiki來***{ctx.author.voice.channel}***放音樂了***')
            await self.wavelink_handler.playMusic(ctx, youtube_url)
        else:
            await ctx.send('**kiki不知道該去哪放音樂**')
        ##titles = self.music_bot.add_queue(ctx, youtube_url)
        ##if titles:
        ##    for title in titles:
        ##        await ctx.reply(f"加入清單: {title}")
        ##await self.music_bot.play_music()

#    @commands.hybrid_command(name='kiki切歌', help='kiki會幫你切歌')
#    async def stop_music(self, ctx: commands.Context):
#        ##current_music_title = self.music_bot.stop_music()
#        ##await ctx.reply(f'***kiki把[{current_music_title}]切掉了***')
#        await ctx.channel.send('test')

    @commands.hybrid_command(name='調整音樂音量', help='可以調整音量大小(0-100)')
    async def set_volume(self, ctx: commands.Context, volume: int):
        await ctx.defer()
        if volume < 0 or volume > 100:
            await ctx.send(f'**{volume}** ??? 有人在皮喔')
            return
        
        await self.wavelink_handler.setVolume(volume)
        if volume > 0:
            await ctx.send(f'已調整音樂音量: {volume}')
        else:
            await ctx.send(f'**kiki閉嘴了**')

    @commands.hybrid_command(name='設定自動播放', help='可以設定要不要隨機自動播放下一首歌')
    async def set_auto_play(self, ctx: commands.Context, is_auto_play: bool):
        await ctx.defer()
        await self.wavelink_handler.setAutoPlay(is_auto_play)
        await ctx.send(f'已設定自動播放: {is_auto_play}')


async def setup(command_bot: commands.Bot):
    await command_bot.add_cog(MusicCommands(command_bot))
