import discord
from discord.ext import commands

class CustomGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, list1, list2):
        team1 = ''
        team2 = ''
        for i,x in enumerate(list1):
            team1 = team1+f"{i}. {x}\n"
        for i,x in enumerate(list2):
            team2 = team2+f"{i}. {x}\n"
        embed  = discord.Embed(title =  "Custom Teams")
        embed.add_field(name = "Team 1", value = team1, inline = True)
        embed.add_field(name = "Team 2", value = team2, inline = True)
        return embed

    @commands.command()
    async def custom(self, ctx, *args):
        embed = self.create_embed(args[:len(args)//2], args[len(args)//2:])
        await ctx.send(embed = embed)

async def setup(bot):
    await bot.add_cog(CustomGames(bot))