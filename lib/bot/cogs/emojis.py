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

    def get_emoji_ids(self, user_id, guild_id, emojis):
        emoji_ids = []
        for emoji in emojis:
            with db.Session() as session:
                emoji_entry = session.query(db.UserEmoji).join(db.Emoji, db.UserEmoji.emoji_id == db.Emoji.id).filter(
                    db.UserEmoji.user_id == user_id,
                    db.UserEmoji.emoji_name == f':{emoji}:',
                    db.Emoji.guild_id != guild_id
                ).first()
                if emoji_entry:
                    emoji_ids.append(emoji_entry.emoji_id)
        return emoji_ids

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        emojis = self.extract_emojis(message.content)
        emoji_ids = self.get_emoji_ids(message.author.id, message.guild.id, emojis)
        if not emoji_ids:
            return
        await message.delete()
        webhook = discord.utils.get(await message.channel.webhooks(), name='busty pewpew')
        if webhook is None:
            webhook = await message.channel.create_webhook(name='busty pewpew')
        await webhook.send(content=self.new_message(message.content, message.author.id, emojis), username=message.author.display_name, avatar_url=message.author.avatar.url)
    
    @emoji.command(name='tutorial', description='Open a tutorial menu to use emojis')
    async def emoji_tutorial(self, interaction:Interaction):
        embed = discord.Embed(
        title="🤖 Emoji Bot Tutorial",
        description="Welcome to Emoji Bot! This bot enhances your Discord experience by providing a variety of emojis for your server.",
        color=0x3498db
        )
        await interaction.response.send_message(embed=embed)
        embed = discord.Embed(color=0x3498db).add_field(name="**1. Adding Emoji**", value="To add an emoji to your personal stash, use the \n`/emoji add :<emoji_name>: <new_name>` command (`<new_name>` is optional).\nExample: `/emoji add :skull:`.\nYou can also add and use animated emojis.\nThe emoji you are adding should be present in the server where this command is executed.\nAfter adding the emoji, you can use it in any server where this bot is present.").set_image(url="https://media.discordapp.net/attachments/1199589417136955432/1199589537496711248/2024-01-24-10-46-17_meFeshg7-ezgif.com-video-to-gif-converter.gif?ex=65c317d1&is=65b0a2d1&hm=f8c16fbffc4f43418b8c70bd625d1431761e81968794daee88d15566517c34ec&=")
        await interaction.channel.send(embed=embed)
        embed = discord.Embed(color=0x3498db).add_field(name="**2. Using Emoji**", value="To use an emoji, simply type `:<emoji_name>:` in your message.\nExample: `:happy:`\n").set_image(url="https://cdn.discordapp.com/attachments/1199589417136955432/1199589536662044713/2024-01-24-10-48-48_kqiDJuMV-ezgif.com-video-to-gif-converter.gif?ex=65c317d0&is=65b0a2d0&hm=672738009774f0c64b50ec028d487268771ae88f180186b7524ed1c48f847ca9&")
        await interaction.channel.send(embed=embed)
        embed = discord.Embed(color=0x3498db).add_field(name="**3. Listing Emoji**", value="To list all the emojis in your personal stash, use the `/emoji list` command.", inline = False)
        embed.add_field(name="**4. Removing Emoji**", value="To remove an emoji from your personal stash, use the `/emoji remove <emoji_name>` command.\nExample: `/emoji remove :skull:`" , inline = False)
        embed.add_field(name="**5. Emoji Id**", value="To get the id of all the emojis in the server, use the `/emoji id` command.", inline = False)
        await interaction.channel.send(embed=embed)

    @emoji.command(name='id', description='Shows id of all the emojis in the server')
    async def emoji_id(self, interaction:Interaction):
        embed = discord.Embed(title="Emoji id", description='\n'.join(f"\{emoji}" for emoji in interaction.guild.emojis), color=discord.Color.blurple()).set_thumbnail(url=self.bot.user.avatar)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @emoji.command(name='add', description='Add a personal emoji')
    async def emoji_add(self, interaction:Interaction, emoji: str = None, name: str = None):
        if self.has_spaces(emoji) or self.has_spaces(name) or not emoji:
            return await interaction.response.send_message("Invalid emoji name", ephemeral=True)
        try:
            emoji = self.extract_emojis(emoji)[0]
        except IndexError:
            return await interaction.response.send_message("Not found", ephemeral=True)
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
            emoji_entry = session.query(db.Emoji).filter_by(id=emoji_id).first()
            if not emoji_entry:
                emoji_entry = db.Emoji(id=emoji_id, guild=guild_entry)
                session.add(emoji_entry)
            user_emoji_entry = db.UserEmoji(user=user_entry, emoji=emoji_entry, emoji_name=name)
            session.add(user_emoji_entry)
            session.commit()
        await interaction.response.send_message(f"{emoji_id} Emoji added", ephemeral=True)
                
    @emoji.command(name='remove', description='Remove a personal emoji')
    async def emoji_remove(self, interaction:Interaction, emoji_name:str = None):
        if emoji_name is None or self.has_spaces(emoji_name):
            return await interaction.response.send_message("Invalid emoji name", ephemeral=True)
        if emoji_name[0] == '<' and emoji_name[-1] == '>':
            emoji_name = emoji_name.split(':')[1]
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