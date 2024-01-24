from sqlalchemy import create_engine, Column, ForeignKey, String, Integer, select, join
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
    emoji_name = Column(String, nullable=True)
    emoji_id = Column(String, ForeignKey('emoji.id'))

def create_tables():
    Base.metadata.create_all(engine)

create_tables()