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
        logger.info(f'Guilds: {len(self.guilds)}')
        for cog in settings.COGS:
            await bot.load_extension('lib.bot.cogs.'+cog)
        print('Bot ready')

bot = MyBot(command_prefix = settings.PREFIX, intents = intents)

@bot.command()
async def sync(ctx) -> None:
    if ctx.author.id not in settings.OWNER_IDS:
        return
    logger.info(f'synced {len(await bot.tree.sync())} commands')