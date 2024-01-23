import discord
from discord.ext import commands
import lib.bot.settings as settings
from discord import app_commands, Interaction

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Greetings commands"

    @commands.hybrid_command(name='hello', aliases=['hi'], description='Say hello to the bot')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, name="spawn-island")
        if channel is None:
            return
        embed = discord.Embed(title=f"Welcome to {guild.name}!", description=f"Welcome {member.mention} to {guild.name}! Enjoy your stay!", color=discord.Color.green()).set_thumbnail(url=guild.icon).set_author(name=member.name, icon_url=member.avatar)
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, name="spawn-island")
        if channel is None:
            return
        embed = discord.Embed(title=f"Goodbye {member.name}!", description=f"{member.name} has left {guild.name}!", color=discord.Color.red()).set_thumbnail(url=guild.icon).set_author(name=member.name, icon_url=member.avatar)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Greetings(bot))