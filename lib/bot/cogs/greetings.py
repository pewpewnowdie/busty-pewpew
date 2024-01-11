import discord
from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}!')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong! ' + str(round(ctx.bot.latency*1000)) + 'ms')

async def setup(bot):
    await bot.add_cog(Greetings(bot))