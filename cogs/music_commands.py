import asyncio
import discord
import wavelink
import re
from discord.ext import commands
from lib.handler.wavelink_handler import WavelinkHandler

YOUTUBE_PLAYLIST_REGEX = re.compile(r'(?:list=)([a-zA-Z0-9_-]+)')

class MusicCommands(commands.Cog):

    def __init__(self, client=discord.Client):
        self.client = client
        self.wavelink_handler : WavelinkHandler = WavelinkHandler(self.client)
        self.playing_channel : discord.StageChannel = None
        self.text_channel : discord.TextChannel = None
        self.playing_track : str = ''

    async def update_presence(self, presence_text: str):
        self.presence_text = presence_text
        custom_activity = discord.CustomActivity(self.presence_text)
        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.wavelink_handler.connect()

    @commands.hybrid_command(name='kiki放音樂', help='kiki會幫你放音樂')
    async def play_music(self, ctx: commands.Context, 網址: str, 插播: bool = False):
        if (ctx.author.voice is not None):
            await ctx.defer()
            message = await ctx.send('處理音樂請求中……')

            #check if query contains list
            is_playList = bool(YOUTUBE_PLAYLIST_REGEX.search(網址))
            if (is_playList):
                view = YesNoButtons() 
                question_message = await ctx.interaction.followup.send('**kiki發現網址帶有播放清單!** 要把所有音樂都加入播放清單嗎?', view=view, ephemeral=True)
                await view.wait()
                if (view.result is None):
                    await message.delete()
                    await question_message.edit(content='**你放音樂放到睡著ㄌ嗎??**', view=None)
                    return
                is_playList = view.result
                await question_message.delete()

            
            reply_text = ''
            target_channel = ctx.author.voice.channel
            await self.wavelink_handler.joinChannel(client=self.client, voice_channel=target_channel)
            if (target_channel != self.playing_channel):
                await ctx.channel.send(f'kiki來***{ctx.author.voice.channel}***放音樂了')
            self.playing_channel = target_channel
            self.text_channel = ctx.channel
            tracks = await self.wavelink_handler.searchMusic(網址)
            if (tracks is None):
                reply_text = '❌ 找不到音樂！'
            else:
                add_music_text = await self.wavelink_handler.addMusic(tracks, 插播, is_playList)
                if (add_music_text is None):
                    reply_text = '❌ 播放器錯誤！'
                else:
                    reply_text = add_music_text
                    result = await self.wavelink_handler.playMusic()
                    if (result is False):
                        reply_text = '❌ 播放器錯誤！'
            await message.edit(content=reply_text)
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

    @commands.hybrid_command(name='音樂暫停', help='可以暫停/恢復播放的音樂')
    async def pause_music(self, ctx: commands.Context):
        await ctx.defer()
        if (self.playing_track is not None):
            is_paused = not self.wavelink_handler.player.paused
            await self.wavelink_handler.pauseMusic(is_paused)
            if (is_paused):
                await ctx.send(f'**kiki按下了暫停鍵**')
                await self.update_presence('喵喵')
            else:
                await ctx.send(f'🎶 繼續播放：{self.playing_track.title}')
                await self.update_presence(f'🎵 {self.playing_track.title}')
        else:
            await ctx.send('Unstoppable!')

    @commands.hybrid_command(name='調整音樂音量', help='可以調整音量大小(0-100)')
    async def set_volume(self, ctx: commands.Context, 音量: int):
        await ctx.defer()
        if 音量 < 0 or 音量 > 100:
            await ctx.send(f'**{音量}** ??? 有人在皮喔')
            return
        
        await self.wavelink_handler.setVolume(音量)
        if 音量 > 0:
            await ctx.send(f'kiki把音量調到了 **{音量}**')
        else:
            await ctx.send(f'**kiki閉嘴了**')

    @commands.hybrid_command(name='設定自動播放', help='可以設定要不要隨機自動播放下一首歌')
    async def set_auto_play(self, ctx: commands.Context, 自動播放: bool = True):
        await ctx.defer()
        await self.wavelink_handler.setAutoPlay(自動播放)
        await ctx.send(f'已設定自動播放: {自動播放}')

    @commands.hybrid_command(name='查看播放清單', help='可以看播放清單裡的歌')
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
        self.playing_track = payload.track
        await self.text_channel.send(f'🎶 現在播放：{self.playing_track.title}\n{self.playing_track.uri}')
        await self.update_presence(f'🎵 {self.playing_track.title}')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload):
        if (await self.wavelink_handler.on_wavelink_track_end(payload) is False):
            self.playing_track = None
            await self.update_presence('喵喵')

#discord button
class YesNoButtons(discord.ui.View):
    def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.result: bool = None

    @discord.ui.button(label="💚 是", style=discord.ButtonStyle.green)
    async def confirm_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = True
        await interaction.response.edit_message(content="以播放清單加入，處理請求中……", view=None)
        self.stop()

    @discord.ui.button(label="❤️ 否", style=discord.ButtonStyle.red)
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = False
        await interaction.response.edit_message(content="單曲加入，處理請求中……", view=None)
        self.stop()

async def setup(command_bot: commands.Bot):
    await command_bot.add_cog(MusicCommands(command_bot))
