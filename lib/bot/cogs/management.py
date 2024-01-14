import discord
from discord import app_commands
from discord.ext import commands
import lib.bot.settings as settings

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='kick', description='Kick a user from the server')
    async def kick(self, interaction:discord.Interaction, member: discord.Member, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        if member.id in settings.OWNER_IDS:
            await interaction.response.send_message('You cannot kick a bot owner', ephemeral=True)
            return
        if member.id == self.bot.user.id:
            await interaction.response.send_message('You cannot kick me', ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message('You cannot kick someone with a higher role than me', ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(f'Kicked {member.mention}\nReason: {reason}')
    
    @app_commands.command(name='ban', description='Ban a user from the server')
    async def ban(self, interaction:discord.Interaction, member: discord.Member, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        await member.ban(reason=reason)
        await interaction.response.send_message(f'Banned {member.mention}\nReason: {reason}')

    @app_commands.command(name='unban', description='Unban a user from the server')
    async def unban(self, interaction:discord.Interaction, member_id:str, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        user = await self.bot.fetch_user(member_id)
        try:
            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(f'Unbanned {user.mention}\nReason: {reason}')
        except discord.NotFound:
            await interaction.response.send_message('User not found', ephemeral=True)
            
    @app_commands.command(name='purge', description='Purge messages from a channel')
    async def purge(self, interaction:discord.Interaction, amount:int=5):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount+1)

async def setup(bot):
    await bot.add_cog(Management(bot))