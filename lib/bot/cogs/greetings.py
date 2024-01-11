import discord
from discord.ext import commands
from discord import app_commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(fmt)} commands.")

    @commands.hybrid_command()
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}!')

    @commands.hybrid_command()
    async def ping(self, ctx):
        await ctx.send('pong! ' + str(round(self.bot.latency*1000)) + 'ms')

async def setup(bot):
    await bot.add_cog(Greetings(bot))