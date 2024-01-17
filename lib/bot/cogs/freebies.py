import discord
from discord.ext import commands, tasks
from discord import app_commands, Interaction
import pickle
from lib.scraper.freebies_scraper import scraper
import lib.bot.settings as settings

logger = settings.logging.getLogger('bot')

class Freebies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_freebies.start()

    def cog_unload(self) -> None:
        self.update_freebies.stop()

    async def new_freebies(self, game_list, new_game_list):
        logger.info("New freebies")
        for guild in self.bot.guilds:
            channel = discord.utils.get(guild.channels, name="freebies")
            if channel is None:
                continue
            await channel.send([game for game in new_game_list if game not in game_list])

    @tasks.loop(hours=1)
    async def update_freebies(self):
        file = open('lib/scraper/game_list.pickle', 'rb')
        game_list = pickle.load(file)
        file.close()
        new_game_list = scraper.get_freebies()
        if game_list == new_game_list:
            logger.info("No new freebies")
            return
        await self.new_freebies(game_list,new_game_list)
        file = open('lib/scraper/game_list.pickle', 'wb')
        pickle.dump(new_game_list, file)
        file.close()

    @app_commands.command(name="freebies", description="Get a list of freebies")
    async def freebies(self, interaction:Interaction):
        file = open('lib/scraper/game_list.pickle', 'rb')
        game_list = pickle.load(file)
        await interaction.response.send_message(game_list)

async def setup(bot):
    await bot.add_cog(Freebies(bot))