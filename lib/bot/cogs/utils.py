import discord
from discord import Interaction
from discord.ext import commands
from discord.ui import View, Select
import lib.bot.settings as settings

logger = settings.logging.getLogger('bot')

class HelpSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(placeholder="Select a category", options=[discord.SelectOption(label=cog_name, value=cog.description) for cog_name, cog in bot.cogs.items()])

    async def callback(self, interaction:Interaction):
        cog = discord.utils.get(self.bot.cogs.values(), description=self.values[0])
        commands = []
        for command in cog.walk_commands():
            commands.append(command)
        for command in cog.walk_app_commands():
            commands.append(command)
        embed = discord.Embed(title=f"{cog.__cog_name__} Commands", description='\n'.join(f"**/{command.name}** : {command.description}" for command in commands), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Helpful commands"

    @commands.hybrid_command(name='help', description='Lists the commands of the bot')
    async def help(self, ctx:commands.Context):
        embed = discord.Embed(title="Help", description="list of all commands", color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        view = View().add_item(HelpSelect(self.bot))
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name='ping', description='Check the bot\'s latency')
    async def ping(self, ctx):
        await ctx.send('pong! ' + str(round(self.bot.latency*1000)) + 'ms')
    
    @commands.command(name='emoji_id_all', description='Shows id of all the emojis in the server')
    async def emoji_id_all(self, ctx:commands.Context):
        embed = discord.Embed(title="Emoji id", description='\n'.join(f"\{emoji}" for emoji in ctx.guild.emojis), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name='avatar', description='Shows the avatar of a user')
    async def avatar(self, ctx:commands.Context, user:discord.User=None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(title=f"{user.name}'s avatar", color=discord.Color.blurple()).set_image(url=user.avatar)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))