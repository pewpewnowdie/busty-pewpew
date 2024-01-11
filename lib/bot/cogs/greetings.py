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

    @app_commands.command()
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello {interaction.user.mention}!')

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message('pong! ' + str(round(self.bot.latency*1000)) + 'ms')

async def setup(bot):
    await bot.add_cog(Greetings(bot))