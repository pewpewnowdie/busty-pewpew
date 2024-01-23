import discord
from discord.ext import commands
from discord import app_commands, Interaction

class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Don't have Nitro? No problem! Use these emojis instead!"

    emoji = app_commands.Group(name='emoji', description='Don\'t have Nitro? No problem! Use these emojis instead!')

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
                    continue
                webhook = await message.channel.create_webhook(name='busty pewpew')
                await message.delete()
                await webhook.send(content=emoji, username=message.author.display_name, avatar_url=message.author.avatar.url)
                await webhook.delete()
                return
    
    @emoji.command(name='tutorial', description='Open a tutorial menu to use emojis')
    async def emoji_tutorial(self, interaction:Interaction):
        pass

    @emoji.command(name='id', description='Shows id of all the emojis in the server')
    async def emoji_id_all(self, ctx:commands.Context):
        embed = discord.Embed(title="Emoji id", description='\n'.join(f"\{emoji}" for emoji in ctx.guild.emojis), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        await ctx.send(embed=embed, ephemeral=True)

    @emoji.command(name='add', description='Add a personal emoji')
    async def emoji_add(self, interaction:Interaction, emoji: str = None, name: str = None):
        pass

    @emoji.command(name='remove', description='Remove a personal emoji')
    async def emoji_remove(self, interaction:Interaction, name: str = None):
        pass

    @emoji.command(name='list', description='List your personal emojis')
    async def emoji_list(self, interaction:Interaction):
        pass

    @emoji.command(name='rename', description='Rename a personal emoji')
    async def emoji_rename(self, interaction:Interaction, name: str = None, new_name: str = None):
        pass

async def setup(bot):
    await bot.add_cog(Emojis(bot))