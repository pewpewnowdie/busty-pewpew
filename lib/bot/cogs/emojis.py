import discord
from discord.ext import commands
from discord import app_commands, Interaction
import re
import lib.db.db as db

class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Don't have Nitro? No problem! Use these emojis instead!"

    emoji = app_commands.Group(name='emoji', description='Don\'t have Nitro? No problem! Use these emojis instead!')
    
    def extract_emojis(self,message):
        emoji_pattern = re.compile(r':([^:\s]+):')
        emojis = re.findall(emoji_pattern, message)
        # message_without_emojis = re.sub(emoji_pattern, '{}', message)
        return emojis
    
    def new_message(self, message:discord.Message, user_id, emojis):
        new_message = message
        for emoji in emojis:
            new_message = new_message.replace(f':{emoji}:', self.get_emoji_id(user_id, emoji), 1)
        return new_message
    
    def has_spaces(self, input_string):
        if not input_string:
            return False
        pattern = re.compile(r'\s')
        match = re.search(pattern, input_string)
        return bool(match)
    
    def get_emoji_id(self, user_id, emoji):
        with db.Session() as session:
            emoji_entry = session.query(db.UserEmoji).filter_by(user_id=user_id,emoji_name=f':{emoji}:').first()
            if not emoji_entry:
                return None
            return emoji_entry.emoji_id

    def get_emoji_ids(self, user_id, emojis):
        emoji_ids = []
        for emoji in emojis:
            with db.Session() as session:
                emoji_entry = session.query(db.UserEmoji).filter_by(user_id=user_id, emoji_name=f':{emoji}:').first()
                if not emoji_entry:
                    continue
                emoji_ids.append(emoji_entry.emoji_id)
        return emoji_ids

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        emojis = self.extract_emojis(message.content)
        emoji_ids = self.get_emoji_ids(message.author.id, emojis)
        if not emoji_ids:
            return
        await message.delete()
        webhook = await message.channel.create_webhook(name='busty pewpew')
        await webhook.send(content=self.new_message(message.content, message.author.id, emojis), username=message.author.display_name, avatar_url=message.author.avatar.url)
        await webhook.delete()
    
    @emoji.command(name='tutorial', description='Open a tutorial menu to use emojis')
    async def emoji_tutorial(self, interaction:Interaction):
        pass

    @emoji.command(name='id', description='Shows id of all the emojis in the server')
    async def emoji_id_all(self, ctx:commands.Context):
        embed = discord.Embed(title="Emoji id", description='\n'.join(f"\{emoji}" for emoji in ctx.guild.emojis), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        await ctx.send(embed=embed, ephemeral=True)

    @emoji.command(name='add', description='Add a personal emoji')
    async def emoji_add(self, interaction:Interaction, emoji: str = None, name: str = None):
        if self.has_spaces(emoji) or self.has_spaces(name) or not emoji:
            return await interaction.response.send_message("Invalid emoji name", ephemeral=True)
        emoji = self.extract_emojis(emoji)[0]
        if not name:
            name = emoji
        emoji = discord.utils.get(interaction.guild.emojis, name=emoji)
        if not emoji:
            return await interaction.response.send_message("Invalid emoji", ephemeral=True)
        if name[0] != ':' or name[-1] != ':':
            name = f":{name}:"
        with db.Session() as session:
            existing_entry = session.query(db.User).filter_by(id=interaction.user.id).first()
            if not existing_entry:
                user_entry = db.User(id=interaction.user.id)
                session.add(user_entry)
            else:
                user_entry = existing_entry
            existing_entry = session.query(db.UserEmoji).filter_by(user_id=interaction.user.id, emoji_name=name).first()
            if existing_entry:
                await interaction.response.send_message("Emoji already exists", ephemeral=True)
                return
            guild_entry = session.query(db.Guild).filter_by(id=str(emoji.guild.id)).first()
            if not guild_entry:
                guild_entry = db.Guild(id=str(emoji.guild.id))
                session.add(guild_entry)
            if emoji.animated:
                emoji_id = f'<a:{emoji.name}:{emoji.id}>'
            else:
                emoji_id = f'<:{emoji.name}:{emoji.id}>'
            emoji_entry = db.Emoji(id=emoji_id, guild=guild_entry)
            session.add(emoji_entry)
            user_emoji_entry = db.UserEmoji(user=user_entry, emoji=emoji_entry, emoji_name=name)
            session.add(user_emoji_entry)
            session.commit()
        await interaction.response.send_message(f"{emoji_id} Emoji added", ephemeral=True)
                

    @emoji.command(name='remove', description='Remove a personal emoji')
    async def emoji_remove(self, interaction:Interaction, emoji_name:str=None):
        if emoji_name is None or self.has_spaces(emoji_name):
            return await interaction.response.send_message("Invalid emoji name", ephemeral=True)
        if emoji_name[0] != ':' or emoji_name[-1] != ':':
            emoji_name = f":{emoji_name}:"
        with db.Session() as session:
            emoji_entry = session.query(db.UserEmoji).filter_by(user_id=interaction.user.id, emoji_name=emoji_name).first()
            if not emoji_entry:
                return await interaction.response.send_message("Emoji doesn't exist", ephemeral=True)
            session.delete(emoji_entry)
            session.commit()
            await interaction.response.send_message("Emoji removed", ephemeral=True)

    @emoji.command(name='list', description='List your personal emojis')
    async def emoji_list(self, interaction:Interaction):
        with db.engine.connect() as con:
            sql = db.select(db.UserEmoji).where(db.UserEmoji.user_id == interaction.user.id)
            result = con.execute(sql)
            emojis = []
            for row in result:
                emoji = {'name': row[3], 'id': row[2]}
                emojis.append(emoji)
            if not emojis:
                embed = discord.Embed(title="Personal emojis", description="You don't have any personal emojis", color=discord.Color.blurple()).set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar)
            else:
                embed = discord.Embed(title="Personal emojis", description='', color=discord.Color.blurple()).set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar)
                for emoji in emojis:
                    name = emoji['name']
                    id = emoji['id']
                    embed.add_field(name='', value=f"{name} {id}", inline=False)
            await interaction.response.send_message(embed=embed)

    @emoji.command(name='rename', description='Rename a personal emoji')
    async def emoji_rename(self, interaction:Interaction, name: str = None, new_name: str = None):
        pass

async def setup(bot):
    await bot.add_cog(Emojis(bot))