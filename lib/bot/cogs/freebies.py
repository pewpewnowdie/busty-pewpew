import discord
from discord.ext import commands, tasks
from discord import app_commands, Interaction
import pickle
from lib.scraper.freebies_scraper import scraper
import lib.bot.settings as settings

logger = settings.logging.getLogger('discord')

class Freebies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Freebies for you to claim now!!"
        self.update_freebies.start()

    def cog_unload(self) -> None:
        self.update_freebies.stop()

    def create_embed(self, game_list):
        embed = discord.Embed(title="Freebies", description="Here are the current freebies", color=0x00ff00)
        emojis = {'2Game': '<:2Game:1197226115413057627>', 'Allyouplay': '<:Allyouplay:1197226167409848453>', 'Amazon.com': '<:Amazon:1197226180345081856>', 'Battle.net': '<:Battle:1197226191178956920>', 'CDKeys.com': '<:CDKeys:1197226202096730132>', 'DLGamer.com': '<:DLGamer:1197226216357363822>', 'Dreamgame': '<:Dreamgame:1197226228646682724>', 'Driffle': '<:Driffle:1197226242752122890>', 'Ea.com': '<:Ea:1197226255246962699>', 'EGAMING': '<:EGAMING:1197226276017160266>', 'Eneba': '<:Eneba:1197226290130985160>', 'Epic Games Store': '<:EpicGamesStore:1197226302701326346>', 'eTail.Market EU': 
'<:eTail:1197226320967520368>', 'eTail.Market UK': '<:eTail:1197226320967520368>', 'eTail.Market USA': '<:eTail:1197226320967520368>', 'Fanatical': '<:Fanatical:1197226357801894041>', 'G2A': '<:G2A:1197226398411132959>', 'G2Play': '<:G2Play:1197226411677712404>', 'Gamebillet': '<:Gamebillet:1197226426710114304>', 'GamersGate': '<:GamersGate:1197226438881980466>', 'GameSeal': '<:GameSeal:1197226452538626058>', 'GAMESLOAD': '<:GAMESLOAD:1197226466048491633>', 'Gamesplanet DE': '<:GamesplanetDE:1197226484767670352>', 'Gamesplanet FR': '<:GamesplanetDE:1197226484767670352>', 'Gamesplanet UK': '<:GamesplanetDE:1197226484767670352>', 'Gamesplanet US': '<:GamesplanetDE:1197226484767670352>', 'GAMIVO': '<:GAMIVO:1197226498189447299>', 'Gog.com': '<:Gog:1197226513616089170>', 'Green Man Gaming': '<:GreenManGaming:1197226534998642688>', 'HRK Game': '<:HRKGame:1197226548005187704>', 'Humble Store': '<:HumbleStore:1197226565038252162>', 'Indie Gala Store': '<:IndieGalaStore:1197226582125842492>', 'Instant Gaming': '<:InstantGaming:1197226594004115617>', 'JoyBuggy': '<:JoyBuggy:1197226611758608384>', 'K4G.com': '<:K4G:1197226632440721660>', 'Kinguin': '<:Kinguin:1197226643480137798>', 'Microsoft Store': '<:MicrosoftStore:1197226653986861107>', 'MMOGA': '<:MMOGA:1197226672408236062>', 'MTCGame': '<:MTCGame:1197226685230219305>', 'Newegg': '<:Newegg:1197226696127021149>', 'Noctre': '<:Noctre:1197226711478194296>', 'Nuuvem': '<:Nuuvem:1197226725378101328>', 'Play-Asia': '<:PlayAsia:1197226737994571838>', 'PlayStation Store': '<:PlayStationStore:1197226748929134602>', 'PremiumCDKeys.com': '<:PremiumCDKeys:1197226759607816342>', 'Punktid': '<:Punktid:1197226770735304805>', 'Rockstar Store': '<:RockstarStore:1197226782340947968>', 'Steam': '<:Steam:1197226793996931215>', 'Ubisoft Store': '<:UbisoftStore:1197226804767891556>', 'Voidu': '<:Voidu:1197226815043944499>', 'WinGameStore': '<:WinGameStore:1197226826481807440>', 'Yuplay': '<:Yuplay:1197235967531155507>'}
        for game in game_list:
            game_title = game['title']
            shop_link = game['shop-link']
            old_price = game['price-old']
            duration = game['duration']
            try:
                emoji = emojis[game['shop-name']]
            except KeyError:
                emoji = '\grey-question'
            if duration is None:
                duration = "No end date"
            embed.add_field(name='',value=f'{emoji} **[{game_title}]({shop_link})**\n~~{old_price}~~\t{duration}', inline=False)
        return embed

    async def new_freebies(self, fresh_games):
        logger.info("New freebies found")
        for guild in self.bot.guilds:
            channel = discord.utils.get(guild.channels, name="freebies")
            if channel is None:
                continue
            await channel.send(embed=self.create_embed(fresh_games))

    @tasks.loop(hours=1)
    async def update_freebies(self):
        file = open('lib/scraper/game_list.pickle', 'rb')
        game_list = pickle.load(file)
        file.close()
        new_game_list = scraper.get_freebies()
        logger.info(game_list)
        logger.info(new_game_list)
        fresh_games = [game for game in new_game_list if game not in game_list]
        logger.info(fresh_games)
        if fresh_games == [] or fresh_games is None:
            logger.info("No new freebies found")
        else:
            await self.new_freebies(fresh_games)
        file = open('lib/scraper/game_list.pickle', 'wb')
        pickle.dump(new_game_list, file)
        file.close()

    @app_commands.command(name="freebies", description="Get a list of freebies")
    async def freebies(self, interaction:Interaction):
        file = open('lib/scraper/game_list.pickle', 'rb')
        game_list = pickle.load(file)
        await interaction.response.send_message(embed=self.create_embed(game_list))

async def setup(bot):
    await bot.add_cog(Freebies(bot))