import discord
from discord.ext import commands
import lib.bot.settings as settings

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Greetings commands"

    @commands.hybrid_command(name='hello', aliases=['hi'], description='Say hello to the bot')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}!')

    @commands.hybrid_command(name='ping', description='Check the bot\'s latency')
    async def ping(self, ctx):
        await ctx.send('pong! ' + str(round(self.bot.latency*1000)) + 'ms')

async def setup(bot):
    await bot.add_cog(Greetings(bot))