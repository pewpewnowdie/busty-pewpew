import discord
from discord import app_commands, Interaction
from discord.ext import commands
import lib.bot.settings as settings

logger = settings.logging.getLogger('bot')

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def log(self, interaction:Interaction, embed):
        guild = interaction.guild
        log_channel = discord.utils.get(guild.channels, name="logs")
        try:
            await log_channel.send(embed=embed)
        except Exception:
            logger.error("'logs' channel not found, or bot missing permissions")

    def create_embed(self, func, user, reason, interaction:Interaction):
        embed = discord.Embed()
        embed.set_author(name=f"[{func}] {user.name}", icon_url=user.avatar)
        embed.add_field(name = "User", value = f"{user.mention}", inline = True)
        embed.add_field(name = "Moderator", value = f"{interaction.user.mention}", inline = True)
        embed.add_field(name = "Reason", value = f"{reason}", inline = True)
        embed.add_field(name = "Channel", value = f"<#{interaction.channel.id}>", inline = False)
        return embed

    @app_commands.command(name='kick', description='Kick a user from the server')
    async def kick(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
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
        embed = self.create_embed('KICK', member, reason, interaction)
        await interaction.response.send_message(embed=embed)
        await self.log(interaction,embed)
    
    @app_commands.command(name='ban', description='Ban a user from the server')
    async def ban(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        await member.ban(reason=reason)
        embed = self.create_embed('BAN', member, reason, interaction)
        await interaction.response.send_message(embed=embed)
        await self.log(interaction,embed)

    @app_commands.command(name='unban', description='Unban a user from the server')
    async def unban(self, interaction:Interaction, member_id:str, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        user = await self.bot.fetch_user(member_id)
        try:
            await interaction.guild.unban(user, reason=reason)
            embed=self.create_embed('UNBAN', user, reason, interaction)
            await interaction.response.send_message(embed=embed)
            await self.log(interaction,embed)
        except discord.NotFound:
            await interaction.response.send_message('User not found', ephemeral=True)
        
    @app_commands.command(name='purge', description='Purge messages from a channel')
    async def purge(self, interaction:Interaction, amount:int=5):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        embed = discord.Embed()
        embed.set_author(name=f"[PURGE] {interaction.user.name}", icon_url=interaction.user.avatar)
        embed.add_field(name=f"{amount} message(s) in", value=f"<#{interaction.channel.id}>")
        await self.log(interaction,embed=embed)
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount+1)

    @app_commands.command(name='mute', description='Mute a user')
    async def mute(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        if member.id in settings.OWNER_IDS:
            await interaction.response.send_message('You cannot mute a bot owner', ephemeral=True)
            return
        if member.id == self.bot.user.id:
            await interaction.response.send_message('You cannot mute me', ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message('You cannot mute someone with a higher role than me', ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name='Muted')
        if role is None:
            role = await interaction.guild.create_role(name='Muted')
            for channel in interaction.guild.channels:
                await channel.set_permissions(role, send_messages=False)
        if role not in member.roles:
            embed=self.create_embed('MUTE', member, reason, interaction)
            await interaction.response.send_message(embed=embed)
            await self.log(interaction,embed)
            await member.add_roles(role, reason=reason)
        else:
            await interaction.response.send_message('User is already muted', ephemeral=True)

    @app_commands.command(name='unmute', description='Unmute a user')
    async def unmute(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
        if interaction.user.id not in settings.OWNER_IDS:
            await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name='Muted')
        if role is None:
            await interaction.response.send_message('User is not muted', ephemeral=True)
            return
        if role not in member.roles:
            await interaction.response.send_message('User is not muted', ephemeral=True)
            return
        await member.remove_roles(role, reason=reason)
        embed = self.create_embed('UNMUTE', member, reason, interaction)
        await interaction.response.send_message(embed=embed)
        await self.log(interaction,embed)

async def setup(bot):
    await bot.add_cog(Management(bot))