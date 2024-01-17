import discord
from discord import app_commands, Interaction
from discord.ext import commands
import lib.bot.settings as settings
from datetime import timedelta

logger = settings.logging.getLogger('bot')

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Commands for managing the server"
    
    def is_admin(interaction:Interaction):
        if discord.utils.get(interaction.guild.roles, name="Admin") in interaction.user.roles:
            return True
        return False

    async def log(self, interaction:Interaction, embed):
        guild = interaction.guild
        log_channel = discord.utils.get(guild.channels, name="audit-logs")
        try:
            await log_channel.send(embed=embed)
        except Exception:
            logger.error(f"'audit-logs' channel not found, or bot missing permissions in {interaction.guild.name}")

    def create_embed(self, func, user, reason, interaction:Interaction):
        embed = discord.Embed().set_author(name=f"[{func}] {user.name}", icon_url=user.avatar).add_field(name = "User", value = f"{user.mention}", inline = True).add_field(name = "Moderator", value = f"{interaction.user.mention}", inline = True).add_field(name = "Reason", value = f"{reason}", inline = True).add_field(name = "Channel", value = f"<#{interaction.channel.id}>", inline = False)
        return embed

    @app_commands.command(name='kick', description='Kick a user from the server')
    @app_commands.check(is_admin)
    async def kick(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
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
        await member.send(embed=discord.Embed(title=f"You have been kicked from {interaction.guild.name}", description=f"Reason: {reason}", color=discord.Color.red()).set_thumbnail(url=interaction.guild.icon))
        await self.log(interaction,embed)
    @kick.error
    async def kick_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)
    
    @app_commands.command(name='ban', description='Ban a user from the server')
    @app_commands.check(is_admin)
    async def ban(self, interaction:Interaction, member: discord.Member, *, reason:str=None):
        await member.ban(reason=reason)
        embed = self.create_embed('BAN', member, reason, interaction)
        await interaction.response.send_message(embed=embed)
        await member.send(embed=discord.Embed(title=f"You have been banned from {interaction.guild.name}", description=f"Reason: {reason}", color=discord.Color.red()).set_thumbnail(url=interaction.guild.icon))
        await self.log(interaction,embed)
    @ban.error
    async def ban_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)

    @app_commands.command(name='unban', description='Unban a user from the server')
    @app_commands.check(is_admin)
    async def unban(self, interaction:Interaction, member_id:str, *, reason:str=None):
        user = await self.bot.fetch_user(member_id)
        try:
            await interaction.guild.unban(user, reason=reason)
            embed=self.create_embed('UNBAN', user, reason, interaction)
            await interaction.response.send_message(embed=embed)
            await self.log(interaction,embed)
        except discord.NotFound:
            await interaction.response.send_message('User not found', ephemeral=True)
    @unban.error
    async def unban_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)
        
    @app_commands.command(name='purge', description='Purge messages from a channel')
    @app_commands.check(is_admin)
    async def purge(self, interaction:Interaction, amount:int=5):
        embed = discord.Embed().set_author(name=f"[PURGE] {interaction.user.name}", icon_url=interaction.user.avatar).add_field(name=f"{min(amount,50)} message(s) in", value=f"<#{interaction.channel.id}>")
        await self.log(interaction,embed=embed)
        await interaction.response.defer()
        await interaction.channel.purge(limit=min(amount+1,50))
    @purge.error
    async def purge_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)

    @app_commands.command(name='timeout', description='Timeout a user')
    @app_commands.check(is_admin)
    async def timeout(self, interaction:Interaction, member: discord.Member, *, reason:str=None, minutes:int=1):
        if member.id in settings.OWNER_IDS:
            await interaction.response.send_message('You cannot mute a bot owner', ephemeral=True)
            return
        if member.id == self.bot.user.id:
            await interaction.response.send_message('You cannot mute me', ephemeral=True)
            return
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message('You cannot mute someone with a higher role than me', ephemeral=True)
            return
        embed=discord.Embed().set_author(name=f"[TIMEOUT] {member.name}", icon_url=member.avatar).add_field(name = "User", value = f"{member.mention}", inline = True).add_field(name = "Moderator", value = f"{interaction.user.mention}", inline = True).add_field(name = "Reason", value = f"{reason}", inline = True).add_field(name = "Channel", value = f"<#{interaction.channel.id}>", inline = False).add_field(name = "Duration", value = f"{minutes} minute(s)", inline = True)
        await interaction.response.send_message(embed=embed)
        await member.send(embed=discord.Embed(title=f"You have been timed out in {interaction.guild.name} for {minutes} min", description=f"Reason: {reason}", color=discord.Color.red()).set_thumbnail(url=interaction.guild.icon))
        await self.log(interaction,embed)
        await member.timeout(timedelta(minutes=minutes), reason=reason)
    @timeout.error
    async def timeout_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)

    @app_commands.command(name='giverole', description='Give a role to a user')
    @app_commands.check(is_admin)
    async def giverole(self, interaction:Interaction, member: discord.Member, role: discord.Role):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message('You cannot give a role higher than me', ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message('User already has this role', ephemeral=True)
            return
        await member.add_roles(role)
        embed = discord.Embed().set_author(name=f"[GIVE ROLE] {member.name}", icon_url=member.avatar).add_field(name = "User", value = f"{member.mention}", inline = True).add_field(name = "Moderator", value = f"{interaction.user.mention}", inline = True).add_field(name = "Role", value = f"{role.mention}", inline = True).add_field(name = "Channel", value = f"<#{interaction.channel.id}>", inline = False)
        await interaction.response.send_message(embed=embed)
        await self.log(interaction,embed)
    @giverole.error
    async def giverole_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)
    
    @app_commands.command(name='takerole', description='Take a role from a user')
    @app_commands.check(is_admin)
    async def takerole(self, interaction:Interaction, member: discord.Member, role: discord.Role):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message('You cannot take a role higher than me', ephemeral=True)
            return
        if role not in member.roles:
            await interaction.response.send_message('User does not have this role', ephemeral=True)
            return
        await member.remove_roles(role)
        embed = discord.Embed().set_author(name=f"[TAKE ROLE] {member.name}", icon_url=member.avatar).add_field(name = "User", value = f"{member.mention}", inline = True).add_field(name = "Moderator", value = f"{interaction.user.mention}", inline = True).add_field(name = "Role", value = f"{role.mention}", inline = True).add_field(name = "Channel", value = f"<#{interaction.channel.id}>", inline = False)
        await interaction.response.send_message(embed=embed)
        await self.log(interaction,embed)
    @takerole.error
    async def takerole_error(self, interaction:Interaction, error):
        await interaction.response.send_message('You do not have permission to use this command', ephemeral=True)
        logger.info(error)

async def setup(bot):
    await bot.add_cog(Management(bot))