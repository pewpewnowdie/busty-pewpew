import lib.bot.settings as settings
import discord
from discord.ext import commands
from discord import app_commands

logger = settings.logging.getLogger('bot')

intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self, command_prefix:str, intents:discord.Intents, **kwargs):
        super().__init__(command_prefix = command_prefix, intents = intents, **kwargs)

    def run(self):
        print('Running bot...')
        super().run(settings.DISCORD_API_SECRET, root_logger=True)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=settings.MY_GUILD)
        await self.tree.sync(guild=settings.MY_GUILD)

    async def on_ready(self) -> None:
        logger.info(f'User: {self.user.name} - {self.user.id}')

        await bot.load_extension('lib.bot.cogs.greetings')
        # await bot.load_extension('lib.bot.cogs.custom_games')
        
        print('Bot ready')

bot = MyBot(command_prefix = settings.PREFIX, intents = intents)