from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, select
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

db = 'sqlite:///lib/db/database.db'
engine = create_engine(db, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    user_emoji = relationship('UserEmoji', backref='user')

class Guild(Base):
    __tablename__ = 'guild'
    id = Column(String, primary_key=True)
    setting = relationship('GuildSetting', backref='guild')
    emoji = relationship('Emoji', backref='guild')

class Emoji(Base):
    __tablename__ = 'emoji'
    id = Column(String, primary_key=True)
    guild_id = Column(String, ForeignKey('guild.id'))
    user_emoji = relationship('UserEmoji', backref='emoji')

class GuildSetting(Base):
    __tablename__ = 'guild_setting'
    guild_id = Column(String, ForeignKey('guild.id'), primary_key=True)
    prefix = Column(String, nullable=True)
    log_channel_id = Column(String, nullable=True)
    welcome_channel_id = Column(String, nullable=True)
    freebie_channel_id = Column(String, nullable=True)
    admin_role_id = Column(String, nullable=True)

class UserEmoji(Base):
    __tablename__ = 'user_emoji'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.id'))
    emoji_id = Column(String, ForeignKey('emoji.id'))
    emoji_name = Column(String, nullable=True)

def create_tables():
    Base.metadata.create_all(engine)
    
# guild = Guild(id = '1195611167805153391')
# session.add(guild)
    
# setting = GuildSetting(guild=guild, prefix='!', welcome_channel_id='1196743047787053097', freebie_channel_id='1197144575597363342', admin_role_id='1196465390381977680')
# session.add(setting)
    
# user = User(id='467620259982213130')
# session.add(user)

# emoji = Emoji(id = '<a:yourmom:1199035021441388554>', guild=guild)
# session.add(emoji)

# ue = UserEmoji(user=user, emoji=emoji, emoji_name='yomum')
# session.add(ue)
# session.commit()
    
# smt = select(UserEmoji).where(UserEmoji.user_id == '467620259982213130')
# with engine.connect() as conn:
#     result = conn.execute(smt)
#     print(result.fetchone()[2])

create_tables()