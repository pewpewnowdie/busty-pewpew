import discord
from discord.ext import commands

class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Don't have Nitro? No problem! Use these emojis instead!"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content[0] == ':' and message.content[-1] == ':':
            for guild in self.bot.guilds:
                if guild == message.guild:
                    continue
                emoji = discord.utils.get(guild.emojis, name=message.content[1:-1])
                if not emoji:
                    return
                webhook = await message.channel.create_webhook(name='busty pewpew')
                await message.delete()
                await webhook.send(content=emoji, username=message.author.display_name, avatar_url=message.author.avatar.url)
                await webhook.delete()
                return
    
async def setup(bot):
    await bot.add_cog(Emojis(bot))