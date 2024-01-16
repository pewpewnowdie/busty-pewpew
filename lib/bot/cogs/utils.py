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
        embed = discord.Embed(title=f"{cog.__cog_name__} Commands", description='\n'.join(f"**{command.name}**: {command.description}" for command in commands), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
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

async def setup(bot):
    await bot.add_cog(Utils(bot))