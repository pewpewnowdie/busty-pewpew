import lib.bot.settings as settings
import discord
from discord.ext import commands
from discord import app_commands

logger = settings.logging.getLogger('bot')

intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self, command_prefix:str, intents:discord.Intents, **kwargs):
        super().__init__(command_prefix = command_prefix, intents = intents, help_command=None, **kwargs)

    def run(self):
        print('Running bot...')
        super().run(settings.DISCORD_API_SECRET, root_logger=True)

    async def on_ready(self) -> None:
        logger.info(f'User: {self.user.name} - {self.user.id}')

        await bot.load_extension('lib.bot.cogs.greetings')
        # await bot.load_extension('lib.bot.cogs.custom_games')
        await bot.load_extension('lib.bot.cogs.management')
        
        print('Bot ready')

bot = MyBot(command_prefix = settings.PREFIX, intents = intents)

@bot.command()
async def sync(ctx) -> None:
    if ctx.author.id not in settings.OWNER_IDS:
        return
    logger.info(await bot.tree.sync())

@bot.hybrid_command(name='help', description='Lists the commands of the bot')
async def help(ctx):
    embed = discord.Embed(title="Help", description="list of all commands", color=discord.Color.blurple()).set_thumbnail(url=bot.user.avatar)

    for slash_command in bot.tree.walk_commands():
        embed.add_field(name=slash_command.name, value=slash_command.description if slash_command.description else slash_command.name, inline=False) 

    await ctx.send(embed=embed)