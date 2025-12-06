import discord
from discord.ext import commands
from main import join_voice_channel, leave_voice_channel


class BasicCommands(commands.Cog):

    def __init__(self, client=discord.Client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Command Bot 登入身分: {self.client.user}')
        custom_activity = discord.CustomActivity('喵喵')
        await self.client.change_presence(status=discord.Status.online, activity=custom_activity)
        try:
            synced = await self.client.tree.sync()
            print(f'Synced {synced} commands')
        except Exception as e:
            print('An error occurred while syncing: ', e)

    @commands.hybrid_command(name='kiki', help='kiki會跟你打招呼')
    async def kiki(self, ctx: commands.Context):
        await ctx.defer()
        await ctx.send('喵喵喵')

    @commands.hybrid_command(name='kiki來', help='可以叫kiki進頻道')
    async def kiki_come(self, ctx: commands.Context):
        await ctx.defer()
        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                await leave_voice_channel(self.client, ctx.voice_client.channel)
            await join_voice_channel(self.client, ctx.author.voice.channel)
            await ctx.send('喵')
        else:
            await ctx.send('**kiki不知道你想叫她去哪**')        

    @commands.hybrid_command(name='kiki滾', help='無情ㄉ趕走kiki')
    async def kiki_fuck_off(self, ctx: commands.Context):
        await ctx.defer()
        if (ctx.voice_client is not None) and (ctx.author.voice is not None) and (ctx.voice_client.channel == ctx.author.voice.channel):
            await leave_voice_channel(self.client, ctx.voice_client.channel)
            await ctx.send(':(')
        else:
            await ctx.send('||誰在狗叫||')


async def setup(command_bot: commands.Bot):
    await command_bot.add_cog(BasicCommands(command_bot))
